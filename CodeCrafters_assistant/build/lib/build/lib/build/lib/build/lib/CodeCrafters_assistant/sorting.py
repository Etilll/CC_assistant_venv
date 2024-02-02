from CodeCrafters_assistant.utils import Translate
from pathlib import Path


class FileSorter(Translate):
    def __init__(self, parent_class):
        self.parent = parent_class
        self.parent.modules.append(self)
        self.parent.module_chosen = len(self.parent.modules) - 1
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
                                        'input':f"{self.translate_string('enter_input_folder','green')} {path}"},
                                        'output':f"{self.translate_string('enter_output_folder','green')} {path}"}}}
    
        if mode != 'first':
            self.parent.module_chosen = tmp
  
    def starter(self, arg1: str, arg2: str):
        # Створюємо об'єкт Path для директорії джерела
        source_path = Path(arg1)
        # Перевіряємо, чи існує директорія та чи це директорія
        if not source_path.exists() or not source_path.is_dir():
            # Повертаємо повідомлення про помилку, якщо директорія недійсна
            return f"{self.RED}{arg1}{self.translate_string('invalid_path','green')}"

        # Створюємо об'єкт Path для директорії призначення
        destination_path = Path(arg2)
        # Перевіряємо, чи існує директорія та чи це директорія
        if not destination_path.exists() or not destination_path.is_dir():
            # Повертаємо повідомлення про помилку, якщо директорія недійсна
            return f"{self.RED}{arg2}{self.translate_string('invalid_path','green')}"

        # Якщо директорії коректні, викликаємо метод real_sorter з правильними директоріями
        self.real_sorter(source_path, destination_path)

    def real_sorter(self, path: Path, output: Path):
        import shutil
        RETURN_TUPLE = self.sorter(path)
        for categories, unnamed in RETURN_TUPLE[0].items():
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
        for em_folder in RETURN_TUPLE[1]:
            try:
                em_folder.rmdir()
            except OSError:
                print(f'Error during remove folder {em_folder}')

    def sorter(self, path: Path):
        ALL_LISTS = {}
        FOLDERS = []
        for file in path.iterdir():
            if not file.is_dir():
                file_name = file.name
                known = False
                suff = Path(file_name).suffix[1:].upper()
                for check,category in self.known_formats.items():
                    if suff == check:
                        dir_dict = self.known_formats[check] + "_list"
                        if not dir_dict in ALL_LISTS:
                            ALL_LISTS[dir_dict] = {}
                        if not suff in ALL_LISTS[dir_dict]:
                            ALL_LISTS[dir_dict][suff] = []
                        
                        ALL_LISTS[dir_dict][suff].append(path / file_name)
                        known = True

                if known != True:
                    self.known_formats[suff] = 'unknown'
                    if not 'unknown_list' in ALL_LISTS:
                        ALL_LISTS['unknown_list'] = {}

                    ALL_LISTS['unknown_list'][suff] = []
                    ALL_LISTS['unknown_list'][suff].append(path / file_name)
                
            elif file.is_dir() and (file.name not in ('archives', 'video', 'audio', 'documents', 'images', 'unknown')):
                FOLDERS.append(path / file.name)
                self.sorter(path / file.name)

        FOLDERS.append(path)
        return ALL_LISTS, FOLDERS

    def normalize(self, name: str, suff="") -> str:
        from re import sub
        translate_name = sub(r'\W', '_', name.translate(self.translate))
        translate_name += suff
        return translate_name