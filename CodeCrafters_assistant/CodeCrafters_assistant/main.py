from CodeCrafters_assistant.utils import IdFormat, Translate
from CodeCrafters_assistant.contact_book import ContactBook
from CodeCrafters_assistant.notes import NoteBook
from CodeCrafters_assistant.sorting import FileSorter
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import xml.etree.ElementTree as ET
import pathlib

class InputManager(IdFormat, Translate):
    def __init__(self):
        # Тут завантажуємо дані з файла (якщо він є. Якщо немає - викликаємо функцію, що його створить і заповнить "скелетом" даних для збереження)
        # Тут же ініціалізуємо технічні змінні для цього класу.
        self.languages = {0:"en",1:"ua",2:"ru"}
        self.languages_local = {0:'English',1:'Українська',2:'Русский'}
        import locale
        #system_language = locale.getdefaultlocale()[0].lower().split('_')
        system_language = locale.getlocale()[0].lower().split('_')
        tree = None
        if system_language[0] in self.languages.values():
            tree = ET.parse(f"{pathlib.Path(__file__).parent.resolve()}/localization_{system_language[0]}.xml")
        else:
            tree = ET.parse(f"{pathlib.Path(__file__).parent.resolve()}/localization_en.xml")
        self.localization = tree.getroot()
        self.module_chosen = None
        self.command = 'change_language'
        self.modules = []
        self.contactbook = ContactBook(self)
        self.notepad = NoteBook(self)
        self.sorter = FileSorter(self)
        
        self.reinit(mode='first')
        
        self.current_module_commands = []
        self.menu_delay = None

    def reinit(self, mode=None):
        if mode != 'first':
            self.contactbook.reinit()
            self.notepad.reinit()
            self.sorter.reinit()
        self.actions = {}
        self.technical_actions = {}
        self.technical_actions['default'] = {}
        self.actions = self.action_filler(self.modules)
        tmp = None
        if mode != 'first' and self.module_chosen != None:
            tmp = self.module_chosen
        self.confirm = ['y','yes']
        self.confirm.append(self.translate_string('confirm').lower())
        self.confirm.append(self.translate_string('confirm_long').lower())
        self.deny = ['n','no']
        self.deny.append(self.translate_string('deny').lower())
        self.deny.append(self.translate_string('deny_long').lower())
        self.stop = [self.translate_string('stop').lower()]
        self.actions['default'] = {}
        self.actions['default']["change_language"] = { 
                                           'description':"change_language_desc", 
                                            'methods':{self.print_languages:{},
                                                       self.set_language:{
                                                           'lang':self.translate_string('select_language','cyan')}}}
        self.actions['default']["change_module"] = {
                                           'description':"change_module_desc", 
                                            'methods':{self.print_modules:{},
                                                       self.set_module:{
                                                           'module_id':self.translate_string('select_module','cyan')}}}
        self.actions['default']["leave"] = {
                                           'description':"exit", 
                                            'methods':{self.say_goodbye:{},
                                                       quit:{}}}

        if mode != 'first':
            self.module_chosen = tmp
        else:
            self.module_chosen = None

    def set_language(self,lang):
        try:
            lang = self.input_to_id(lang)
            if lang in self.languages.keys():
                tree = ET.parse(f"{pathlib.Path(__file__).parent.resolve()}/localization_{self.languages[lang]}.xml")
                self.localization = tree.getroot()
                self.reinit()
            else:
                return self.translate_string('wrong_id_error','yellow')
            
            print(self.translate_string('assistant_welcome','green'))
        except ValueError:
            return self.translate_string('wrong_id_error','yellow')

    
    def print_languages(self):
        string = self.translate_string('change_language_list','green')
        string += '\n' + '\n'.join(f'{self.RED}{key}{self.GREEN}. {value}' for key, value in self.languages_local.items()) + '\n'
        print(string)
    
    def print_modules(self):
        self.module_chosen = None
        string = self.translate_string('print_module_p0','green') + ':\n'
        string += '\n'.join(f"{self.RED}{self.modules.index(key)}{self.GREEN}. {self.translate_string('print_module_p1')} {self.translate_string(key.method_table['__localization']['name'],'red','green',mode=self.modules.index(key))} {self.translate_string('print_module_p2')} '{self.RED}{self.modules.index(key)}{self.GREEN}' {self.translate_string('print_module_p3')}" for key in self.modules) + '\n'
        print(string)

    def set_module(self,module_id):
        try:
            module_id = self.input_to_id(module_id)
            if type(module_id) == int and module_id < len(self.modules):
                self.module_chosen = module_id
                self.actions['default']["back"] = {
                                            'description':"change_module_desc", 
                                                'methods':{self.reset_module:{}}}
                self.current_module_commands = []
                for script in self.actions[self.module_chosen].keys():
                    self.current_module_commands.append(script) 
                
                self.current_module_commands.append("cancel")
                for script in self.actions['default'].keys():
                    self.current_module_commands.append(script) 

                self.command_completer = WordCompleter(self.current_module_commands)
                self.command = ''
            elif type(module_id) == str:
                print(module_id)
            else:
                print(self.translate_string('wrong_module_number','yellow','green'))
        except ValueError:
            print(self.translate_string('wrong_module_number','yellow','green'))


    def reset_module(self):
            self.current_module_commands = []
            self.module_chosen = None
            del self.actions['default']["back"] 
    
    # Список actions автоматично заповнюється командами з відповідних класів (окрім загальних команд, таких як 'help', 'exit', тощо - вони записуються напряму, у _init__() класу Input_manager).
    # У кожного класу, що має певні консольні команди, є поле self.method_table - 
    # в ньому і зберігається назва консольної команди, відповідний метод і екземпляр класу, а також локалізація тексту (що програма буде казати користувачеві перед отриманням аргументів).
    def action_filler(self, modules):
        actions_dict = {}
        filler_ids = -1
        for item in modules:
            if hasattr(item, 'method_table') and item.method_table != {}:
                filler_ids += 1
                actions_dict[modules.index(item)] = {}
                self.technical_actions[modules.index(item)] = {}
                for com_name,parameters in item.method_table.items():
                    if com_name != '__localization':
                        if 'technical' in parameters.keys():
                            self.technical_actions[modules.index(item)][com_name] = parameters
                        else:
                            actions_dict[modules.index(item)][com_name] = parameters

        return actions_dict
    
    def main(self):
        while True:
            if self.menu_delay:
                while True: 
                    self.command = input(f"{self.translate_string('enter_back_p0','cyan')} {self.translate_string('enter_back_p1','red','cyan')}{self.translate_string('enter_back_p2')}:   {self.RED}")
                    if self.command.lower() in self.confirm:
                        self.menu_delay = None
                        break
            if self.command == '':
                if self.module_chosen != None:
                    string = f"{self.translate_string('menu_entered_p0','green')} {self.translate_string(self.modules[self.module_chosen].method_table['__localization']['name'], 'red', 'green')}{self.translate_string('menu_entered_p1')}\n"
                    string += "\n".join(f"{'  '}{self.RED}{key}{self.GREEN} - {self.translate_string(value['description'])}" for key, value in self.actions[self.module_chosen].items()) + f"\n{'  '}{self.RED}back{self.GREEN} - {self.translate_string('return_to_main')}. \n{'  '}{self.RED}leave{self.GREEN} - {self.translate_string('exit')}. \n{'  '}{self.RED}cancel{self.GREEN} - {self.translate_string('cancel')}.\n{'_' * 80}"
                    print(string)
        
                    style = Style.from_dict({
                        '': 'fg:ansigreen',

                        'part_1': 'fg:ansicyan',
                    })

                    message = [
                        ('class:part_1', self.translate_string('enter_the_command')),
                    ]
                    self.command = prompt(message, completer=self.command_completer, style=style).strip().lower()
                elif self.module_chosen == None:
                    self.command = 'change_module'
            if self.command != '':
                result = self.start_script(self.command)
                if result == 'leave':
                    break

    # Тут в нас перевіряється, чи це команда класу InputManager, чи ні. Якщо ні - витягуємо необхідні дані зі словника. Ітеруємо словник методів. Якщо у метода немає аргументів, 
    # просто запускаємо його виконання. Якщо аргументи є, то ітеруємо по словнику аргументів, кожного разу видаваючи відповідну текстову фразу, що також є у словнику, і 
    # чекаючи на інпут.
    def start_script(self,command,mode=None):
        scripts = None
        if mode != 'technical':
            scripts = self.actions
        else:
            scripts = self.technical_actions
        category = None
        command_exceptions = ['change_language', 'change_module', 'back', 'leave', 'cancel']
        if type(self.module_chosen) == int and not command in command_exceptions and (command in scripts['default'].keys() or command in scripts[self.module_chosen].keys()):
            self.menu_delay = True
        if type(self.module_chosen) == int:
            if (command in scripts[self.module_chosen].keys()):
                category = self.module_chosen
        if (command in scripts['default'].keys()):
            category = 'default'
        if category != None:
            if type(scripts[category][command]) != dict:
                selected_action = scripts[category][command]
                selected_action()
            else:
                for key,value in scripts[category][command]['methods'].items():
                    if value == {}:
                        result = key()
                        if result == 'abort':
                            return
                    else:
                        arguments_list = []
                        result = ' '
                        while type(result) == str:
                            silent_restart = None
                            for k,v in value.items():
                                while True:
                                    argument = input(f"{self.CYAN}{v}" + f':   {self.RED}')
                                    if argument.strip().lower() == 'leave':
                                        self.say_goodbye()
                                        return 'leave'
                                    if argument.strip().lower() == 'cancel':
                                        silent_restart = True
                                        return
                                    if argument != '':
                                        arguments_list.append(argument)
                                        break
                            if not silent_restart:
                                result = key(*arguments_list)
                                if type(result) == str:
                                    if result == 'abort':
                                        return
                                    arguments_list = []
                                    print(result)
        self.command = ''

    def say_goodbye(self):
        print(self.translate_string('goodbye', 'yellow','default'))

def starter():
    manager = InputManager()
    manager.main()

if __name__ == '__main__':
    starter()