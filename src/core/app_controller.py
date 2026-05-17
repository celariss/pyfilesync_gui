from importlib.resources import path

import flet as ft

from ui.ui_interface import *
from syncconfig import *
from dirsyncer import *


class AppController:
    def __init__(self):
        self.ui:UIInterface = None
        self.config:SyncConfig = SyncConfig()
        self.config_path = ''
        self.recent_files:set[str] = set()
        self._load_parameters()

    def set_ui(self, ui:UIInterface):
        self.ui = ui

    def get_config_path(self):
        return self.config_path

    async def new_project(self):
        self.config = SyncConfig()
        self.config_path = ''
        self.ui.clear_results()
        self.ui.set_config_data(self.config)
        self.ui.refresh()

    async def save_config_file(self, path:str):
        error = self.config.save_file(path)
        if not error:
            self.config_path = path
            self.recent_files.add(path)
            self._save_app_settings()
            self.ui.refresh()

    async def load_config_file(self, path:str):
        config = SyncConfig()
        error = config.load_file(path)
        if error:
            self.ui.show_error("Please fix error in config file : "+error)
        self.config = config
        self.config_path = path
        self.recent_files.add(path)
        self._save_app_settings()
        self.ui.refresh()
        self.ui.set_config_data(self.config)
        self.ui.clear_results()

    async def change_pair(self, pair_index:int,pair:PairSection):
        self.config.pairs[pair_index] = pair
        self.ui.set_config_data(self.config)

    async def add_folders_pair(self):
        self.config.pairs.append(PairSection())
        self.ui.set_config_data(self.config)

    async def remove_folders_pair(self, pair_index:int):
        if pair_index>=0 and pair_index<len(self.config.pairs):
            self.config.pairs.pop(pair_index)
            self.ui.set_config_data(self.config)

    async def remove_recent_file(self, path:str):
        if path in self.recent_files:
            self.recent_files.remove(path)
            self._save_app_settings()
            self.ui.refresh()

    async def run_compare(self, pair_index:int=None):
        self.ui.clear_results()
        for idx, pair in enumerate(self.config.pairs):
            if pair_index is None or idx == pair_index:
                cmpdata:CmpData = DirSyncer.compare_dirs(pair.left, pair.right, include=pair.include_patterns, exclude=pair.exclude_patterns,
                                                compare_file_content=pair.cmp_files_content, ignore_right_only=False,
                                                on_warning=self.on_warning)
                self._add_results(cmpdata, pair, idx)

    async def run_sync(self, pair_index:int=None):
        for idx, pair in enumerate(self.config.pairs):
            if pair_index is None or idx == pair_index:
                pass

    def _save_app_settings(self):
        pathname = os.path.join(os.path.dirname(sys.argv[0]), "parameters.json")
        try:
            params:dict = {
                "recent_files": list(self.recent_files)
            }
            with open(pathname, 'w', encoding='utf8') as f:
                json.dump(params, f, indent=4, ensure_ascii=False)
        except Exception as exc:
            print("Error while saving config file: " + str(exc))

    def _load_parameters(self):
        pathname = os.path.join(os.path.dirname(sys.argv[0]), "parameters.json")
        if os.path.exists(pathname):
            with open(pathname, 'r', encoding='utf8') as f:
                try:
                    result = json.loads(f.read())
                except json.JSONDecodeError as exc:
                    print("Config file is not a valid JSON file")
                    return
                self.recent_files = set(result.get("recent_files", []))

    
    def _add_results(self, cmpdata:CmpData, pair:PairSection, pair_index:int):
        for item in cmpdata.left_only_files.union(cmpdata.left_only_empty_dirs):
            self._add_result(pair.left, item, '', '', pair_index=pair_index)
        for item in cmpdata.right_only_files.union(cmpdata.right_only_dirs):
            self._add_result('', '', pair.right, item, pair_index=pair_index)
        for item in cmpdata.different_files:
            self._add_result(pair.left, item, pair.right, item, pair_index=pair_index)
        self.ui.refresh_results()

    def _add_result(self, left_dir, left_file, right_dir, right_file, pair_index:int):
        result_item = ResultItem(
            status=CmpStatus.LEFT_ONLY if right_dir == '' else (CmpStatus.RIGHT_ONLY if left_dir == '' else CmpStatus.DIFFERENT),
            left_dir=left_dir,
            left_file=left_file,
            right_dir=right_dir,
            right_file=right_file,
            pair_index=pair_index
        )
        #print(f"Appended result: '{left}' | '{right}'")
        self.ui.append_result(result_item)

    def on_warning(self, message):
        print("Warning:", message)

   