# QIDI Max 4 Moonraker metadata boundary snapshot (2026-09-15).
# Copyright (C) 2020 Eric Callahan; GNU GPLv3.
# Extracted storage class and metascan handler; dependencies are supplied by the harness.

class FileManager:
    async def _handle_metascan_request(
        self, web_request: WebRequest
    ) -> Dict[str, Any]:
        async with self.sync_lock:
            requested_file: str = web_request.get_str('filename')
            gcpath = pathlib.Path(self.file_paths["gcodes"]).joinpath(requested_file)
            if not gcpath.is_file():
                raise self.server.error(f"File '{requested_file}' does not exist", 404)
            if gcpath.suffix not in VALID_GCODE_EXTS:
                raise self.server.error(f"File {gcpath} is not a valid gcode file")
            # remove metadata and force a rescan
            ret = self.gcode_metadata.remove_file_metadata(requested_file)
            if ret is not None:
                await ret
            path_info = self.get_path_info(gcpath, "gcodes")
            evt = self.gcode_metadata.parse_metadata(requested_file, path_info)
            await evt.wait()
            metadata: Optional[Dict[str, Any]]
            metadata = self.gcode_metadata.get(requested_file, None)
            if metadata is None:
                raise self.server.error(
                    f"Failed to parse metadata for file '{requested_file}'", 500)
            metadata['filename'] = requested_file
            return metadata


class MetadataStorage:
    def __init__(self,
                 config: ConfigHelper,
                 db: DBComp
                 ) -> None:
        self.server = config.get_server()
        self.enable_object_proc = config.getboolean(
            'enable_object_processing', False)
        self.default_metadata_parser_timeout = config.getfloat(
            'default_metadata_parser_timeout', 20.)
        self.gc_path = ""
        db.register_local_namespace(METADATA_NAMESPACE)
        self.mddb = db.wrap_namespace(
            METADATA_NAMESPACE, parse_keys=False)
        version = db.get_item(
            "moonraker", "file_manager.metadata_version", 0).result()
        if version != METADATA_VERSION:
            # Clear existing metadata when version is bumped
            self.mddb.clear()
            db.insert_item(
                "moonraker", "file_manager.metadata_version",
                METADATA_VERSION)
        # Keep a local cache of the metadata.  This allows for synchronous
        # queries.  Metadata is generally under 1KiB per entry, so even at
        # 1000 gcode files we are using < 1MiB of additional memory.
        # That said, in the future all components that access metadata should
        # be refactored to do so asynchronously.
        self.metadata: Dict[str, Any] = self.mddb.as_dict()
        self.pending_requests: Dict[
            str, Tuple[Dict[str, Any], asyncio.Event]] = {}
        self.busy: bool = False

    def prune_storage(self) -> None:
        # Check for removed gcode files while moonraker was shutdown
        if self.gc_path:
            del_keys: List[str] = []
            for fname in list(self.metadata.keys()):
                fpath = os.path.join(self.gc_path, fname)
                if not os.path.isfile(fpath):
                    del self.metadata[fname]
                    del_keys.append(fname)
                elif "thumbnails" in self.metadata[fname]:
                    # Check for any stale data entries and remove them
                    need_sync = False
                    for thumb in self.metadata[fname]['thumbnails']:
                        if 'data' in thumb:
                            del thumb['data']
                            need_sync = True
                    if need_sync:
                        self.mddb[fname] = self.metadata[fname]
            # Delete any removed keys from the database
            if del_keys:
                ret = self.mddb.delete_batch(del_keys).result()
                self._remove_thumbs(ret)
                pruned = '\n'.join(ret.keys())
                if pruned:
                    logging.info(f"Pruned metadata for the following:\n"
                                 f"{pruned}")

    def update_gcode_path(self, path: str) -> None:
        if path == self.gc_path:
            return
        if self.gc_path:
            self.metadata.clear()
            self.mddb.clear()
        self.gc_path = path

    def get(self,
            key: str,
            default: Optional[_T] = None
            ) -> Union[_T, Dict[str, Any]]:
        return deepcopy(self.metadata.get(key, default))

    def insert(self, key: str, value: Dict[str, Any]) -> None:
        val = deepcopy(value)
        self.metadata[key] = val
        self.mddb[key] = val

    def is_processing(self) -> bool:
        return len(self.pending_requests) > 0

    def is_file_processing(self, fname: str) -> bool:
        return fname in self.pending_requests

    def _has_valid_data(self,
                        fname: str,
                        path_info: Dict[str, Any]
                        ) -> bool:
        if path_info.get('ufp_path', None) is not None:
            # UFP files always need processing
            return False
        if path_info.get('_3mf_path', None) is not None:
            return False
        mdata: Dict[str, Any]
        mdata = self.metadata.get(fname, {'size': "", 'modified': 0})
        for field in ['size', 'modified']:
            if mdata[field] != path_info.get(field, None):
                return False
        return True

    def remove_directory_metadata(self, dir_name: str) -> Optional[Awaitable]:
        if dir_name[-1] != "/":
            dir_name += "/"
        del_items: Dict[str, Any] = {}
        for fname in list(self.metadata.keys()):
            if fname.startswith(dir_name):
                md = self.metadata.pop(fname, None)
                if md:
                    del_items[fname] = md
        if del_items:
            # Remove items from persistent storage
            self.mddb.delete_batch(list(del_items.keys()))
            eventloop = self.server.get_event_loop()
            # Remove thumbs in a nother thread
            return eventloop.run_in_thread(self._remove_thumbs, del_items)
        return None

    def remove_file_metadata(self, fname: str) -> Optional[Awaitable]:
        md: Optional[Dict[str, Any]] = self.metadata.pop(fname, None)
        if md is None:
            return None
        self.mddb.pop(fname, None)
        eventloop = self.server.get_event_loop()
        return eventloop.run_in_thread(self._remove_thumbs, {fname: md})

    def _remove_thumbs(self, records: Dict[str, Dict[str, Any]]) -> None:
        for fname, metadata in records.items():
            # Delete associated thumbnails
            fdir = os.path.dirname(os.path.join(self.gc_path, fname))
            if "thumbnails" in metadata:
                thumb: Dict[str, Any]
                for thumb in metadata["thumbnails"]:
                    path: Optional[str] = thumb.get("relative_path", None)
                    if path is None:
                        continue
                    thumb_path = os.path.join(fdir, path)
                    if not os.path.isfile(thumb_path):
                        continue
                    try:
                        os.remove(thumb_path)
                    except Exception:
                        logging.debug(f"Error removing thumb at {thumb_path}")

    def move_directory_metadata(self, prev_dir: str, new_dir: str) -> None:
        if prev_dir[-1] != "/":
            prev_dir += "/"
        moved: List[Tuple[str, str, Dict[str, Any]]] = []
        for prev_fname in list(self.metadata.keys()):
            if prev_fname.startswith(prev_dir):
                new_fname = os.path.join(new_dir, prev_fname[len(prev_dir):])
                md: Optional[Dict[str, Any]]
                md = self.metadata.pop(prev_fname, None)
                if md is None:
                    continue
                self.metadata[new_fname] = md
                moved.append((prev_fname, new_fname, md))
        if moved:
            source = [m[0] for m in moved]
            dest = [m[1] for m in moved]
            self.mddb.move_batch(source, dest)
            # It shouldn't be necessary to move the thumbnails
            # as they would be moved with the parent directory

    def move_file_metadata(
        self, prev_fname: str, new_fname: str
    ) -> Union[bool, Awaitable]:
        metadata: Optional[Dict[str, Any]]
        metadata = self.metadata.pop(prev_fname, None)
        if metadata is None:
            # If this move overwrites an existing file it is necessary
            # to rescan which requires that we remove any existing
            # metadata.
            if self.metadata.pop(new_fname, None) is not None:
                self.mddb.pop(new_fname, None)
            return False

        self.metadata[new_fname] = metadata
        self.mddb.move_batch([prev_fname], [new_fname])
        return self._move_thumbnails([(prev_fname, new_fname, metadata)])

    async def _move_thumbnails(
        self, records: List[Tuple[str, str, Dict[str, Any]]]
    ) -> None:
        eventloop = self.server.get_event_loop()
        for (prev_fname, new_fname, metadata) in records:
            prev_dir = os.path.dirname(os.path.join(self.gc_path, prev_fname))
            new_dir = os.path.dirname(os.path.join(self.gc_path, new_fname))
            if "thumbnails" in metadata:
                thumb: Dict[str, Any]
                for thumb in metadata["thumbnails"]:
                    path: Optional[str] = thumb.get("relative_path", None)
                    if path is None:
                        continue
                    thumb_path = os.path.join(prev_dir, path)
                    if not os.path.isfile(thumb_path):
                        continue
                    new_path = os.path.join(new_dir, path)
                    new_parent = os.path.dirname(new_path)
                    try:
                        if not os.path.exists(new_parent):
                            os.mkdir(new_parent)
                            # Wait for inotify to register the node before the move
                            await asyncio.sleep(.2)
                        await eventloop.run_in_thread(
                            shutil.move, thumb_path, new_path
                        )
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        logging.exception(
                            f"Error moving thumb from {thumb_path} to {new_path}"
                        )

    def parse_metadata(self,
                       fname: str,
                       path_info: Dict[str, Any]
                       ) -> asyncio.Event:
        if fname in self.pending_requests:
            return self.pending_requests[fname][1]
        mevt = asyncio.Event()
        ext = os.path.splitext(fname)[1]
        if (
            ext not in VALID_GCODE_EXTS or
            self._has_valid_data(fname, path_info)
        ):
            # request already pending or not necessary
            mevt.set()
            return mevt
        self.pending_requests[fname] = (path_info, mevt)
        if self.busy:
            return mevt
        self.busy = True
        event_loop = self.server.get_event_loop()
        event_loop.register_callback(self._process_metadata_update)
        return mevt

    async def _process_3mf_metadata_update(self) -> None:
        while self.pending_requests:
            fname, (path_info, mevt) = \
                list(self.pending_requests.items())[0]
            ufp_path: Optional[str] = path_info.get('ufp_path', None)
            _3mf_path: Optional[str] = path_info.get('_3mf_path', None)
            retries = 3
            while retries:
                try:
                    await self._run_extract_metadata(fname, ufp_path, _3mf_path)
                except Exception:
                    logging.exception("Error running extract_metadata.py")
                    retries -= 1
                else:
                    break
            self.pending_requests.pop(fname, None)
            mevt.set()
        self.busy = False

    def parse_3mf_thumbnail(self,
                            fname: str,
                            path_info: Dict[str, Any]
                            ) -> asyncio.Event:
        if fname in self.pending_requests:
            return self.pending_requests[fname][1]
        mevt = asyncio.Event()
        # ext = os.path.splitext(fname)[1]
        self.pending_requests[fname] = (path_info, mevt)
        if self.busy:
            return mevt
        self.busy = True
        event_loop = self.server.get_event_loop()
        event_loop.register_callback(self._process_3mf_metadata_update)
        return mevt

    async def _process_metadata_update(self) -> None:
        while self.pending_requests:
            fname, (path_info, mevt) = \
                list(self.pending_requests.items())[0]
            if self._has_valid_data(fname, path_info):
                mevt.set()
                continue
            ufp_path: Optional[str] = path_info.get('ufp_path', None)
            _3mf_path: Optional[str] = path_info.get('_3mf_path', None)
            retries = 3
            while retries:
                try:
                    await self._run_extract_metadata(fname, ufp_path, _3mf_path)
                except Exception:
                    logging.exception("Error running extract_metadata.py")
                    retries -= 1
                else:
                    break
            else:
                if ufp_path is None:
                    self.metadata[fname] = {
                        'size': path_info.get('size', 0),
                        'modified': path_info.get('modified', 0),
                        'print_start_time': None,
                        'job_id': None
                    }
                    self.mddb[fname] = self.metadata[fname]
                if _3mf_path is None:
                    self.metadata[fname] = {
                        'size': path_info.get('size', 0),
                        'modified': path_info.get('modified', 0),
                        'print_start_time': None,
                        'job_id': None
                    }
                    self.mddb[fname] = self.metadata[fname]
                logging.info(
                    f"Unable to extract medatadata from file: {fname}")
            self.pending_requests.pop(fname, None)
            mevt.set()
        self.busy = False

    async def _run_extract_metadata(self,
                                    filename: str,
                                    ufp_path: Optional[str],
                                    _3mf_path: Optional[str]
                                    ) -> None:
        # Escape single quotes in the file name so that it may be
        # properly loaded
        filename = filename.replace("\"", "\\\"")
        cmd = " ".join([sys.executable, METADATA_SCRIPT, "-p",
                        self.gc_path, "-f", f"\"{filename}\""])
        timeout = self.default_metadata_parser_timeout
        if ufp_path is not None and os.path.isfile(ufp_path):
            timeout = max(timeout, 300.)
            ufp_path.replace("\"", "\\\"")
            cmd += f" -u \"{ufp_path}\""
        if _3mf_path is not None and os.path.isfile(_3mf_path):
            timeout = max(timeout, 300.)
            _3mf_path.replace("\"", "\\\"")
            cmd += f" -m \"{_3mf_path}\""
        if self.enable_object_proc:
            timeout = max(timeout, 300.)
            cmd += " --check-objects"
        result = bytearray()
        sc: SCMDComp = self.server.lookup_component('shell_command')
        scmd = sc.build_shell_command(cmd, callback=result.extend, log_stderr=True)
        if not await scmd.run(timeout=timeout):
            raise self.server.error("Extract Metadata returned with error")
        try:
            decoded_resp: Dict[str, Any] = jsonw.loads(result.strip())
        except Exception:
            logging.debug(f"Invalid metadata response:\n{result}")
            raise
        path: str = decoded_resp['file']
        metadata: Dict[str, Any] = decoded_resp['metadata']
        if not metadata:
            # This indicates an error, do not add metadata for this
            raise self.server.error("Unable to extract metadata")
        metadata.update({'print_start_time': None, 'job_id': None})
        self.metadata[path] = metadata
        self.mddb[path] = metadata
