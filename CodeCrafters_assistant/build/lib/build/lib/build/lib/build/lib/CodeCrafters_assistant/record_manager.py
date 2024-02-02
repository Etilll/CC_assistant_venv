from CodeCrafters_assistant.utils import Translate
from re import search
from datetime import date,datetime

# Зберігає в собі методи перевірки значень класу Record. Окремо не використовується.
class BirthdayChecks(Translate):
    def month_check(self,month:str):
        if len(month) > 2:
            raise ValueError(self.translate_string('wrong_month_format_char_num','yellow','green'))
        check_month = month
        if month[:1] == "0":
            check_month = month[:1]
        if int(check_month) <= 12:
            return True
        else:
            raise ValueError(self.translate_string('wrong_month_format_out_bound','yellow','green'))

    def day_check(self,day:str):
        if len(day) > 2:
            raise ValueError(self.translate_string('wrong_day_format_char_num','yellow','green'))
        check_day = day
        if day[:1] == "0":
            check_day = day[:1]
        if int(check_day) <= 31:
            return True
        else:
            raise ValueError(self.translate_string('wrong_day_format_out_bound','yellow','green'))

    def year_check(self,year:str):
        if len(year) > 4:
            raise ValueError(self.translate_string('wrong_year_format_char_num','yellow','green'))
        if int(year) <= date.today().year:
            return True
        else:
           raise ValueError(self.translate_string('wrong_year_format_out_bound','yellow','green'))

    def calendar_check(self,year:str,month:str,day:str):
        try:
            if datetime(int(year),int(month),int(day)).date():
                return True
            raise ValueError(self.translate_string('wrong_year_format_days_num','yellow','green'))
        except ValueError:
            raise ValueError(self.translate_string('wrong_year_format_days_num','yellow','green'))

    def birthday_check(self,birthday):
        # Format: MM-DD-YYYY
        if (search(r'\d{2}\D\d{2}\D\d{4}', birthday) != None and len(birthday) == 10):
            month = birthday[0:2]
            day = birthday[3:5]
            year = birthday[6:10]
            if self.month_check(month) and self.day_check(day) and self.year_check(year) and self.calendar_check(year,month,day):
                return birthday
        elif search(r'\d{8}', birthday) != None and len(birthday) == 8:
            month = birthday[0:2]
            day = birthday[2:4]
            year = birthday[4:8]
            if self.month_check(month) and self.day_check(day) and self.year_check(year) and self.calendar_check(year,month,day):
                birthday = birthday[0:2] + "-" + birthday[2:4] + "-" + birthday[4:6] + birthday[6:8]
                return birthday
        else:
            raise ValueError(self.translate_string('wrong_birthday_format','yellow','green'))
        
    def days_to_birthday(self,mode=None):
        if search(r'\d{2}\D\d{2}\D\d{4}', self.data['Birthday']) != None:
            TODAY = date.today()
            tmp = self.data['Birthday']
            BD_DAY = datetime(int(tmp[6:]), int(tmp[0:2]), int(tmp[3:5])).date()
            if (BD_DAY.month < TODAY.month) or ((BD_DAY.month == TODAY.month) and (BD_DAY.day < TODAY.day)):
                BD_DAY = BD_DAY.replace(year = TODAY.year + 1)
            else:
                BD_DAY = BD_DAY.replace(year = TODAY.year)
            if mode == 'no_math':
                return (BD_DAY)
            else:
                return (BD_DAY - TODAY)
        return "None"

class MiscChecks(Translate):
    def p_check(self,phone:str):
        map = {' ':''}
        phone.translate(map)
        if len(phone) == 10 and search(r'\d{10}', phone) != None:
            return phone
        else:
            raise ValueError(self.translate_string('incorrect_phone','yellow','green'))

    def email_check(self,email:str):
        # Format: text@text.text
        if (search(r'\S{3,}@[a-zA-Z]{2,}\.[a-zA-Z]{2,}', email) != None):
            email = f"{email[:email.rfind('@')]}{email[email.rfind('@'):].lower()}"
            return email
        else:
            raise ValueError(self.translate_string('wrong_email_format','yellow','green'))
        
    def has_phone(self,phone:str):
        for i in self.data['Phones'].values():
            if i == phone:
                return True
           
        return False 
    
# Екземпляр класу. Відповідає за зберігання усіх змінних запису. Створюється у ContactBook. Необов'язкові поля можуть бути пропущені символами "n"/"N".
# У самому класі зберігається лише функціонал запису/зміни/видалення. Все інше наслідується від MiscChecks.
class Record(MiscChecks, BirthdayChecks):
    def __init__(self, parent_class):
        self.parent = parent_class
        self.data = {}
        if self.parent:
            self.data = {'Name':self.translate_string('unnamed_contact'),'Birthday':self.translate_string('none'),'Email':self.translate_string('none'),'Address':self.translate_string('none'),'Phones':{}}
        else:
            self.data = {'Name':"Unnamed contact",'Birthday':"None",'Email':"None",'Address':"None",'Phones':{}}

    def __str__(self):
        return f"{self.translate_string('attr_0','red','green')}: {self.data['Name']}; {self.translate_string('attr_1','red','green')}: {self.data['Birthday']}; {self.translate_string('attr_2','red','green')}: {self.data['Email']}; {self.translate_string('attr_3','red','green')}: {self.data['Address']}; {self.translate_string('attr_4','red','green')}: {'; '.join(phone for phone in self.data['Phones'].values())}"

    def record_error(func):
        #print(func.__name__)
        def true_handler(self,arg):
            try:
                result = func(self,arg)
            except ValueError as error_text:
                raise ValueError(error_text)
        return true_handler

    @record_error
    def add_birthday(self,birthday):
        self.data['Birthday'] = self.birthday_check(birthday)

    @record_error
    def add_name(self,name:str):
        self.data['Name'] = name

    @record_error
    def add_email(self,email:str):
        self.data['Email'] = self.email_check(email)

    @record_error
    def add_address(self,address:str):
        self.data['Address'] = address

    def phone_check_and_set(self,mode,phone,new_phone=None):
        try:
            if mode == 'add':
                if phone.lower() == "stop" or phone.lower() in self.parent.stop:
                    return True
                phone = self.p_check(phone)
                self.data['Phones'][len(self.data['Phones'])] = phone
                raise ValueError(f"{self.translate_string('phone_added_p0','yellow','red')}{self.parent.stop[0]}{self.translate_string('phone_added_p2','yellow','green')}")
            elif mode == 'ed':
                if self.has_phone(phone):
                    if type(self.p_check(new_phone)) == str:
                        for phone_id,phone_number in self.data['Phones'].items():
                            if phone_number == phone:
                                self.data['Phones'][phone_id] = new_phone
                                return
                    
                raise ValueError(self.translate_string('phone_not_found','yellow','green'))
            elif mode == 'del':
                if self.has_phone(phone):
                    for phone_id,phone_number in self.data['Phones'].items():
                        if phone_number == phone:
                            del self.data['Phones'][phone_id]
                            print(self.translate_string('phone_removed','yellow','green'))
                            return
                
                raise ValueError(self.translate_string('phone_not_found','yellow','green'))
        except ValueError as error_text:
            raise ValueError(error_text)
            
    def remove_name(self):
        self.data['Name'] = self.translate_string('unnamed_contact')
        print(self.translate_string('name_removed','yellow','green'))

    def remove_birthday(self):
        self.data['Birthday'] = self.translate_string('none')
        print(self.translate_string('birthday_removed','yellow','green'))
    
    def remove_email(self):
        self.data['Email'] = self.translate_string('none')
        print(self.translate_string('email_removed','yellow','green'))

    def remove_address(self):
        self.data['Address'] = self.translate_string('none')
        print(self.translate_string('address_removed','yellow','green'))
        
    def rearrange_phones(self):
        if self.data['Phones'] != {}:
            id_generator = 0
            tmp_array = {}
            for phone in self.data['Phones'].values(): #rearranging phone ids
                tmp_array[id_generator] = phone
                id_generator += 1
            self.data['Phones'] = tmp_array

    def load_data(self,cfg): # To avoid reoccurring checks when loading from storage.bin
        id_generator = 0
        for do_not_use,phone in cfg['Phones'].items(): #rearranging phone ids, just like with contactbook records.
            self.data['Phones'][id_generator] = phone
            id_generator += 1

        self.data['Name'] = cfg['Name']
        self.data['Birthday'] = cfg['Birthday']
        self.data['Email'] = cfg['Email']
        self.data['Address'] = cfg['Address']