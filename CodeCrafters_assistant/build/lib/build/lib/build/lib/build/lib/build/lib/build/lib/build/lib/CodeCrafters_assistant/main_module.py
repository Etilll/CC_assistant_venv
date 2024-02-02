from contact_book import ContactBook
from notes import NoteFile
from sorting import FileSorter
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class HelpMe:
    def help(self):
        # При запуску функції пропонує обрати тему (книга контактів, сортування файлів, тощо). Коли користувач обере тему, видає список команд відповідного класу з self.help_modules
        # Навіщо так? А щоб кожний писав список команд для свого модуля окремо, і редагував у тому ж файлі, одразу ж при внесенні змін або створення нових методів.
        # Тільки не забуваємо перевіряти, щоб назви КОНСОЛЬНИХ команд з вашого модулю не співпадали з назвами з інших модулів.
        help_phrase = {'part_1':{'en':". To see the list of commands for ",'ua':". Щоб подивитись список команд для "},
                       'part_2':{'en':", enter in the console '",'ua':", введіть у консоль '"},
                       'part_3':{'en':"The assistant has the next functions: ",'ua':"Помічник має такі функції: "},
                       'part_4':{'en':"If you want to exit the program, enter '",'ua':"Якщо хочете вийти з програми, напишіть '"},
                       'part_5':{'en':"Please, choose the section number: ",'ua':"Будь ласка, оберіть номер розділу: "},
                       'part_6':{'en':"A list of commands, available for ",'ua':"Список доступних команд для "}}
        func_str = ''
        func_str_p2 = '\n'
        for k,v in self.help_modules.items():
            func_str += self.help_modules[k]['localization']['description'][self.language] + ', '
            func_str_p2 += f"{k}{help_phrase['part_1'][self.language]}{self.help_modules[k]['localization']['name'][self.language]}{help_phrase['part_2'][self.language]}{bcolors.RED}{k}{bcolors.GREEN}'.\n"

        func_str = func_str[:len(func_str)-2]

        general_info = f"{bcolors.GREEN}{'_' * 80}\n{help_phrase['part_3'][self.language]}{func_str}. {func_str_p2}\n{help_phrase['part_4'][self.language]}{bcolors.RED}leave{bcolors.GREEN}'."
        print(general_info)
        while True:
            answer = input(f"{bcolors.CYAN}{help_phrase['part_5'][self.language]}{bcolors.GREEN}").strip().lower()
            if answer in self.help_modules.keys():
                string = f"{'_' * 80}\n{help_phrase['part_6'][self.language]}{self.help_modules[answer]['localization']['name'][self.language]}:\n"
                string += '\n'.join(f'{key} - {value[self.language]}' for key, value in self.help_modules[answer]['scripts'].items()) + f"\n{help_phrase['part_4'][self.language]}{bcolors.RED}leave{bcolors.GREEN}'.\n{'_' * 80}"
                print(string)
                break



class InputManager(HelpMe):
    def __init__(self):
        # Тут завантажуємо дані з файла (якщо він є. Якщо немає - викликаємо функцію, що його створить і заповнить "скелетом" даних для збереження)
        # Тут же ініціалізуємо технічні змінні для цього класу.
        self.help_modules = {}
        self.notepad = NoteFile()
        self.contactbook = ContactBook()
        self.sorter = FileSorter()
        can_have_a_command = [self.contactbook, self.notepad, self.sorter]
        self.actions = self.action_filler(can_have_a_command)
        self.actions['default'] = {}
        self.actions['default']["change_language"] = { 
                                           'description':{
                                               'en':"Sets the programm's language",
                                               'ua':"Встановлює мову програми."}, 
                                            'methods':{self.print_languages:{},
                                                       self.set_language:{
                                                           'lang':{
                                                               'en':f"{bcolors.CYAN}Будь ласка, оберіть мову {bcolors.RED}/{bcolors.CYAN} Please, choose the language",
                                                               'ua':f"{bcolors.CYAN}Будь ласка, оберіть мову {bcolors.RED}/{bcolors.CYAN} Please, choose the language"}}}}
        
        self.actions['default']["change_module"] = {
                                           'description':{
                                               'en':"Allows you to switch to a different menu",
                                               'ua':"Дозволяє переключитись на інше меню."}, 
                                            'methods':{self.print_modules:{},
                                                       self.set_module:{
                                                           'module_id':{
                                                               'en':f"{bcolors.CYAN}Please, choose the menu",
                                                               'ua':f"{bcolors.CYAN}Будь ласка, оберіть меню"}}}}
        
        self.actions['default']["leave"] = quit

        self.current_module_commands = []
        self.module_chosen = None
        self.silent_restart = None
        self.abort = None
        self.menu_delay = None
        self.language = None
        self.languages = {'0':'en','1':'ua'}
        self.languages_local = {'0':'English','1':'Українська'}

    def default_action(self):
        print("Невідома команда. Спробуйте знову, або викликайте команду help щоб отримати допомогу щодо використання програми.")

    def set_language(self,lang):
        try:
            lang = self.input_to_id(lang)
            lang = str(lang)
            if str(lang) in self.languages:
                self.language = self.languages[lang]
                self.contactbook.language = self.languages[lang]
                self.sorter.language = self.languages[lang]
                self.notepad.language = self.languages[lang]
            else:
                self.language = None
                return f"{bcolors.GREEN}Некоректний id. Будь ласка, спробуйте ще раз! {bcolors.RED}/{bcolors.GREEN} Wrong id. Please, try again!"
            
            welcome_phrase = {'en':"Hello! I'm your personal assistant!",'ua':"Привіт! Я ваш персональний помічник."}
            print(f"{bcolors.GREEN}{welcome_phrase[self.language]}")
        except ValueError:
            return f"{bcolors.GREEN}Некоректний id. Будь ласка, спробуйте ще раз! {bcolors.RED}/{bcolors.GREEN} Wrong id. Please, try again!"

    
    def print_languages(self):
        string = f"{bcolors.GREEN}Список доступних мов:  {bcolors.RED}/{bcolors.GREEN}   Languages available:\n"
        string += '\n'.join(f'{bcolors.RED}{key}{bcolors.GREEN}. {value}' for key, value in self.languages_local.items()) + '\n'
        print(string)
    
    def print_modules(self):
        local = {'part_0':{
                    'en':"Available menus",
                    'ua':"Можна перейти у такі меню"},
                'part_1':{
                    'en':"To choose the",
                    'ua':"Щоб обрати меню"},
                'part_2':{
                    'en':"menu, enter '",
                    'ua':"напишіть '"},
                'part_3':{
                    'en':"' in the console.",
                    'ua':"' у консоль."}}
        string = f"{bcolors.GREEN}{local['part_0'][self.language]}:\n"
        string += '\n'.join(f"{bcolors.RED}{key}{bcolors.GREEN}. {bcolors.GREEN}{local['part_1'][self.language]} {bcolors.RED}{self.help_modules[key]['localization']['name'][self.language]}{bcolors.GREEN} {local['part_2'][self.language]}{bcolors.RED}{key}{bcolors.GREEN}{local['part_3'][self.language]}" for key,value in self.help_modules.items()) + '\n'
        print(string)

    def set_module(self,module_id):
        try:
            module_id = self.input_to_id(module_id)
            module_id = str(module_id)
            if module_id in self.help_modules:
                self.module_chosen = module_id
                self.actions['default']["back"] = {
                                            'description':{
                                                'en':"Allows you to switch to a different menu",
                                                'ua':"Дозволяє переключитись на інше меню."}, 
                                                'methods':{self.reset_module:{}}}
                self.current_module_commands = []
                for script in self.actions[self.module_chosen].keys():
                    self.current_module_commands.append(script) 
                
                self.current_module_commands.append("cancel")
                for script in self.actions['default'].keys():
                    self.current_module_commands.append(script) 

                self.command_completer = WordCompleter(self.current_module_commands)
            else:
                error_phrase = {'en':"Wrong module number. Please, try again!",'ua':"Неправильний номер модуля. Спробуйте ще раз!"}
                print(f"{bcolors.YELLOW}{error_phrase[self.language]}")
        except ValueError:
            error_phrase = {'en':"Wrong module number. Please, try again!",'ua':"Неправильний номер модуля. Спробуйте ще раз!"}
            print(f"{bcolors.YELLOW}{error_phrase[self.language]}")


    def reset_module(self):
            self.current_module_commands = []
            self.module_chosen = None
            del self.actions['default']["back"] 
    
    def input_to_id(self, text):
        map = {' ':'','\n':'','\t':'','\r':''}
        new_line = text.translate(map)
        try:
            if int(new_line) >= 0:
                return int(new_line)
            else:
                error_text = {'en':f"{bcolors.YELLOW}An id cannot be a negative number!{bcolors.GREEN}",'ua':f"{bcolors.YELLOW}Id не може бути від'ємним числом!{bcolors.GREEN}"}
                return error_text[self.language]
        except ValueError:
            error_text = {'en':f"{bcolors.YELLOW}Wrong id, try again!{bcolors.GREEN}",'ua':f"{bcolors.YELLOW}Некоректний id, спробуйте ще раз!{bcolors.GREEN}"}
            return error_text[self.language]

    # Список actions автоматично заповнюється командами з відповідних класів (окрім загальних команд, таких як 'help', 'exit', тощо - вони записуються напряму, у _init__() класу Input_manager).
    # У кожного класу, що має певні консольні команди, є поле self.method_table - 
    # в ньому і зберігається назва консольної команди, відповідний метод і екземпляр класу, а також локалізація тексту (що програма буде казати користувачеві перед отриманням аргументів).
    def action_filler(self, can_have_a_command):
        actions_dict = {}
        filler_ids = -1
        for item in can_have_a_command:
            if hasattr(item, 'method_table') and item.method_table != {}:
                filler_ids += 1
                actions_dict[str(can_have_a_command.index(item))] = {}
                for com_name,parameters in item.method_table.items():
                    if com_name != '__localization_insert':
                        actions_dict[str(can_have_a_command.index(item))][com_name] = parameters
                    
                    if 'description' in parameters.keys():
                        conversion_dict = {self.contactbook:'Contact_book', self.notepad:'Note_manager', self.sorter:'Sorter'}
                        if not str(filler_ids) in self.help_modules:
                            self.help_modules[str(filler_ids)] = {'name':conversion_dict[item],'scripts':{},'localization':{}}
                        
                        if com_name != '__localization_insert':
                            self.help_modules[str(filler_ids)]['scripts'][com_name] = parameters['description']
                        else:
                            self.help_modules[str(filler_ids)]['localization']['description'] = parameters['description']
                            self.help_modules[str(filler_ids)]['localization']['name'] = parameters['name']

        return actions_dict
    
    def main(self):

        input_phrase = {
            'part_1':{
                'en':"Please, enter the command:   ",
                'ua':"Будь ласка, введіть необхідну команду:   "},
            'part_3':{
                'en':"If you decide to exit the program, enter '",
                'ua':"Якщо захочете вийти з програми, напишіть '"}}

        while True:
            if self.abort:
                self.abort = None
            if self.menu_delay:
                local = {'en':f"Enter {bcolors.RED}Y/yes{bcolors.CYAN} to return to the previous menu",'ua':f"Напишіть {bcolors.RED}Т/Так{bcolors.CYAN}, щоб повернутися до попереднього меню"}
                delay_commands = {'y', 'yes','так', 'т'}
                while True:
                    command = input(f"{bcolors.CYAN}{local[self.language]}:   {bcolors.RED}")
                    if command.lower() in delay_commands:
                        self.menu_delay = None
                        break
            if self.silent_restart:
                self.silent_restart = None
            command = ''
            if self.language != None:
                if self.silent_restart:
                    pass
                elif self.module_chosen:
                    local = {'part_1':{'en':"You are in the",'ua':"Ви перейшли у меню"},
                             'part_2':{'en':" menu. Available commands list:",'ua':". Список доступних команд:"},
                             'part_3':{'en':"Return to the main menu",'ua':"Повернутися у головне меню"},
                             'part_4':{'en':"Exit the program",'ua':"Вийти з програми"},
                             'part_5':{'en':"Cancels the execution of the current command (e.g. create/edit/sort_files)",'ua':"Скасовує виконання поточної команди (наприклад, create/edit/sort_files)"}}
                    string = f"{bcolors.GREEN}{local['part_1'][self.language]} {bcolors.RED}{self.help_modules[self.module_chosen]['localization']['name'][self.language]}{bcolors.GREEN}{local['part_2'][self.language]}\n"
                    string += "\n".join(f"{'  '}{bcolors.RED}{key}{bcolors.GREEN} - {value[self.language]}" for key, value in self.help_modules[self.module_chosen]['scripts'].items()) + f"\n{'  '}{bcolors.RED}back{bcolors.GREEN} - {local['part_3'][self.language]}. \n{'  '}{bcolors.RED}leave{bcolors.GREEN} - {local['part_4'][self.language]}. \n{'  '}{bcolors.RED}cancel{bcolors.GREEN} - {local['part_5'][self.language]}.\n{'_' * 80}"
                    print(string)
        
                    style = Style.from_dict({
                        '': 'fg:ansigreen',

                        'part_1': 'fg:ansicyan',
                    })

                    message = [
                        ('class:part_1', input_phrase['part_1'][self.language]),
                    ]
                    command = prompt(message, completer=self.command_completer, style=style).strip().lower()
                elif not self.module_chosen:
                    command = 'change_module'
            else:
                command = 'change_language'
 
            # Тут в нас перевіряється, чи це команда класу InputManager, чи ні. Якщо ні - витягуємо необхідні дані зі словника. Ітеруємо словник методів. Якщо у метода немає аргументів, 
            # просто запускаємо його виконання. Якщо аргументи є, то ітеруємо по словнику аргументів, кожного разу видаваючи відповідну текстову фразу, що також є у словнику, і 
            # чекаючи на інпут.
            category = ''
            command_exceptions = ['change_language', 'change_module', 'back', 'leave', 'cancel']        
            if self.module_chosen and not command in command_exceptions and (command in self.actions['default'].keys() or command in self.actions[self.module_chosen].keys()):
                self.menu_delay = True
            if self.module_chosen:
                if (command in self.actions[self.module_chosen].keys()):
                    category = self.module_chosen
            if (command in self.actions['default'].keys()):
                category = 'default'
            if category:
                if type(self.actions[category][command]) != dict:
                    selected_action = self.actions[category][command]
                    selected_action()
                else:
                    for key,value in self.actions[category][command]['methods'].items():
                        if self.abort:
                            break
                        if value == {}:
                            result = key()
                            if result == 'abort':
                                self.abort = True
                        else:
                            arguments_list = []
                            result = ' '
                            while type(result) == str:
                                if self.abort:
                                    break
                                for k,v in value.items():
                                    if self.abort:
                                        break
                                    while True:
                                        if not self.language:
                                            self.language = 'en'
                                        command = input(v[self.language] + f':   {bcolors.RED}')
                                        if command.strip().lower() == 'leave':
                                            self.say_goodbye()
                                            return
                                        if command.strip().lower() == 'cancel':
                                            self.silent_restart = True
                                            self.abort = True
                                            break
                                        if command != '':
                                            arguments_list.append(command)
                                            break
                                if not self.silent_restart:
                                    result = key(*arguments_list)
                                    if type(result) == str:
                                        if result == 'abort':
                                            self.abort = True
                                            arguments_list = []

                                        arguments_list = []
                                        print(result)
                                command = ''

    def say_goodbye(self):
        local = {'en':"Goodbye!",'ua':"До побачення!"}
        print(f'{bcolors.YELLOW}{local[self.language]}{bcolors.DEFAULT}')

def starter():
    manager = InputManager()
    manager.main()

# if __name__ == "__main__":
#     manager = InputManager()
#     manager.main()