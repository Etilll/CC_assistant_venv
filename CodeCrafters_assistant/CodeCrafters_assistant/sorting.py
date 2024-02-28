from CodeCrafters_assistant.utils import Translate
from pathlib import Path
from threading import Thread
import concurrent.futures

class IndexInput:
    def index_input(self, file, path, storage):
        file_name = file.name
        known = False
        suff = Path(file_name).suffix[1:].upper()
        for check in storage.known_formats.keys():
            if suff == check:
                dir_dict = storage.known_formats[check] + "_list"
                if not dir_dict in storage.all_lists:
                    storage.all_lists[dir_dict] = {}
                if not suff in storage.all_lists[dir_dict]:
                    storage.all_lists[dir_dict][suff] = []
                
                storage.all_lists[dir_dict][suff].append(path / file_name)
                known = True

        if known != True:
            storage.known_formats[suff] = 'unknown'
            if not 'unknown_list' in storage.all_lists:
                storage.all_lists['unknown_list'] = {}

            storage.all_lists['unknown_list'][suff] = []
            storage.all_lists['unknown_list'][suff].append(path / file_name)

class FileSorter(Translate, IndexInput):
    def __init__(self, parent_class):
        self.parent = parent_class
        self.parent.modules.append(self)
        self.parent.module_chosen = len(self.parent.modules) - 1
        self.all_lists = {} #Structure: 'category':{'suffix1':['path1', ...], 'suffix2':['path1', ...]}
        self.folders = set()
        self.reinit(mode='first')
        self.categories = { 'images':['JPEG', 'JPG', 'PNG', 'SVG'],
                           'video':['AVI', 'MP4', 'MOV', 'MKV'], 
                           'documents':['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
                           'audio':['MP3', 'OGG', 'WAV', 'AMR'],
                           'archives':['ZIP', 'GZ', 'TAR', 'RAR', '7Z']}
        
        Path('./empty_folder').mkdir(exist_ok=True, parents=True)
        Path('./output_folder').mkdir(exist_ok=True, parents=True)
        CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
        TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")
        self.translate = {}
        for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
            self.translate[ord(cyrillic)] = latin
            self.translate[ord(cyrillic.upper())] = latin.upper()
        
        self.known_formats = {}
        for category,list in self.categories.items():
            for format in list:
                self.known_formats[format] = category


    def reinit(self, mode=None):
        tmp = None
        if type(self.parent.module_chosen) == int:
            tmp = self.parent.module_chosen
        if mode != 'first':
            self.parent.module_chosen = self.parent.modules.index(self)
        path = fr"{self.translate_string('path_p0','red')}  {self.translate_string('path_p1','green')}"
        self.method_table = {'__localization':{
                                'name':'file_sorter_name',
                                'description':'file_sorter_desc'}, 
                            'sort_files':{
                                'description':"sort_files_desc", 
                                'methods':{
                                    self.starter:{
                                        'input':f"{self.translate_string('enter_input_folder','green')} {path}",
                                        'output':f"{self.translate_string('enter_output_folder','green')} {path}"}}}}
    
        if mode != 'first':
            self.parent.module_chosen = tmp
  
    class SorterThread(Thread, IndexInput):
        def __init__(self, parent_class, path, group=None, target=None, name=None, *, daemon=None):
            super().__init__(group=group, target=target, name=name, daemon=daemon)
            self.parent_class = parent_class
            self.path = path

        def run(self) -> None:
            #print("Started a new thread while forming all_list!")
            for file in self.path.iterdir():
                if not file.is_dir():
                    self.index_input(file, self.path,storage=self.parent_class)
                elif file.is_dir() and (file.name not in ('archives', 'video', 'audio', 'documents', 'images', 'unknown')):
                    self.parent_class.folders.add(self.path / file.name)
                    thread = self.parent_class.SorterThread(self.parent_class, self.path / file.name)
                    thread.start()
            if self.parent_class.src != self.path:
                self.parent_class.folders.add(self.path)
        
    def starter(self, arg1: str, arg2: str):
        source_path = Path(arg1)
        # Перевіряємо, чи існує директорія та чи це директорія
        if source_path.exists() and source_path.is_dir():
            self.src = source_path
        else:
            self.src = None
            return f"{self.RED}{arg1}{self.translate_string('invalid_path','green')}"

        destination_path = Path(arg2)
        # Перевіряємо, чи існує директорія та чи це директорія
        if destination_path.exists() and destination_path.is_dir():
            self.dest = destination_path
        else:
            self.dest = None
            return f"{self.RED}{arg2}{self.translate_string('invalid_path','green')}"

        self.input_index_control(self.src)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(self.categories_handler, list(self.all_lists))

        self.folders.add(self.src)
        for em_folder in self.folders:
            try:
                em_folder.rmdir()
            except OSError:
                print(f'Error during remove folder {em_folder}')
        
        self.all_lists = {}
        self.folders = set()

    def categories_handler(self, category):
        output_c = self.dest / str(category[0:len(category)-5])
        if not output_c.exists():
            output_c.mkdir(exist_ok=True, parents=True)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(self.suffixes_handler, list(self.all_lists[category]))

    def suffixes_handler(self, suffix):
        output_e = None
        cat = None
        for category,lisst in self.categories.items():
            if suffix in lisst:
                cat = category
        if cat == None:
            cat = 'unknown'
        output_e = self.dest / cat.lower() / str(suffix)
        if not output_e.exists():
            output_e.mkdir(exist_ok=True, parents=True)
        
        for dir in self.all_lists[f"{cat.lower()}_list"][suffix]:
            file_name = str(dir)
            file_name = file_name[file_name.rfind("\\") + 1:]
            suff = file_name[file_name.rfind("."):]
            file_name = file_name[:len(file_name) - len(file_name[file_name.rfind("."):])]
            dir.replace(output_e / self.normalize(file_name, suff))



    def real_sorter(self, path: Path, output: Path):
        import shutil
        for categories, unnamed in self.all_lists.items():
            output_c = output / str(categories[0:len(categories)-5])
            if not output_c.exists():
                output_c.mkdir(exist_ok=True, parents=True)
            for extension, extlist in unnamed.items():
                output_e = output_c / str(extension)
                if not output_e.exists():
                    output_e.mkdir(exist_ok=True, parents=True)
                for dir in extlist:
                    file_name = str(dir)
                    file_name = file_name[file_name.rfind("\\") + 1:]
                    suff = file_name[file_name.rfind("."):]
                    file_name = file_name[:len(file_name) - len(file_name[file_name.rfind("."):])]
                    if categories != 'archives_list':
                        dir.replace(output_e / self.normalize(file_name, suff))
                    else:
                        tmp_namee = output_e / self.normalize(file_name)
                        try:
                            shutil.unpack_archive(dir, output_e, suff[1:])
                            dir.unlink()
                        except shutil.ReadError:
                            tmp_namee.rmdir()
        for em_folder in self.folders:
            try:
                em_folder.rmdir()
            except OSError:
                print(f'Error during remove folder {em_folder}')
        
        self.all_lists = {}
        self.folders = set()

    def input_index_control(self, path: Path):
        for file in path.iterdir():
            if not file.is_dir():
                self.index_input(file, path, storage=self)
            elif file.is_dir() and (file.name not in ('archives', 'video', 'audio', 'documents', 'images', 'unknown')):
                self.folders.add(path / file.name)
                thread = self.SorterThread(self, path / file.name)
                thread.start()
                #self.input_index_control(path / file.name)

        self.folders.add(path)

    def normalize(self, name: str, suff="") -> str:
        from re import sub
        translate_name = sub(r'\W', '_', name.translate(self.translate))
        translate_name += suff
        return translate_name