import imghdr
import ntpath
import os
import shutil




from PIL import Image
import traceback
import random
import webbrowser
from threading import Thread


from kivy.graphics import Color, Line
from kivy.metrics import Metrics
from kivy.uix.filechooser import FileChooserIconView

from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from indic_transliteration import sanscript, xsanscript
from indic_transliteration.sanscript import transliterate


import requests

from kivy.app import App
from kivy.clock import Clock

from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


import data_capture_lessons
import data_lessons
import image_utils
import certifi
from kivy.utils import platform


# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()


Window.softinput_mode = 'below_target'
from kivy.config import Config


if platform !='android':
    Config.remove_option('input','%(name)s')
    print (Config.items('input'))



class LessonGroupScreen(Screen):
    container = ObjectProperty(None)
    lesson_list_names = []
    def __init__(self,**kwargs):
        super(LessonGroupScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)
        Clock.schedule_once(self.add_buttons,1)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons':
                return False

    def add_buttons(self,dt):
        self.list_groups = data_capture_lessons.get_groups()
        self.container.bind(minimum_height=self.container.setter('height'))
        for element in self.list_groups:
            font_name = "Caveat-Bold.ttf"
            button = Button(text=element[1],font_name=font_name,font_size="50sp",background_color=[0.76,0.83,0.86,0.8],pos_hint={'top': 1},size_hint_y=None,size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0]: self.switch_to_title(instance, a)
            self.lesson_list_names.append(element[1])
            self.container.add_widget(button)

    def switch_to_title(self,i,a):

        self.selected_group = a
        self.manager.current ="lessons"
        self.manager.transition.direction = 'left'

    def launch_popup(self):
        show = ImportPop()
        self.popupWindow = Popup(title="Import Mini Lesson", content=show,
                                 size_hint=(1, 0.7), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self,self.lesson_list_names)
        # open popup window
        self.popupWindow.open()

    def launch_popup_create(self):
        show = CreatePop()
        self.popupWindow = Popup(title="Create Mini Lesson", content=show,
                                 size_hint=(1, 0.8), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self,self.lesson_list_names)
        # open popup window
        self.popupWindow.open()




class LessonListScreen(Screen):


    def __init__(self, **kwargs):
        super(LessonListScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)



    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons':
                self.manager.transition.direction = 'right'
                self.manager.current = self.manager.previous()
                return True


    def on_enter(self, *args):
        groupid = self.manager.get_screen('groups').selected_group
        self.list_lessons = data_capture_lessons.get_Lessons_ofgroup(groupid)
        self.ids.lesson_c.clear_widgets()
        Clock.schedule_once(self.add_buttons, 1)

    def add_buttons(self,dt):
        groupid = self.manager.get_screen('groups').selected_group

        self.list_lessons = data_capture_lessons.get_Lessons_ofgroup(groupid)

        self.button_list = []
        self.ids.lesson_c.bind(minimum_height=self.ids.lesson_c.setter('height'))
        for element in self.list_lessons:
            if element[2] is None or element[2] == "" or element[2] =="English":
                font_name = "Caveat-Bold.ttf"
            else:
                font_name = "unifont.ttf"
            button = Button(text=element[1], font_name = font_name,font_size='50sp',background_color=[0.76, 0.83, 0.86, 0.8], pos_hint={'top': 1},
                            size_hint_y=None, size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0],b=element[2]: self.switch_to_title(instance, a,b)
            self.ids.lesson_c.add_widget(button)
            self.button_list.append(button)

    def launch_popup_import(self):
        show = ImportPop()
        self.popupWindow = Popup(title="Import Mini Lesson", content=show,
                            size_hint=(1, 0.4),auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self)
        # open popup window
        self.popupWindow.open()

    def switch_to_title(self, i, a,b):
        self.selected_lesson = a
        if b is None or b == "" or b == "English":
            self.manager.set_font("Caveat-Bold.ttf")
        else:
            self.manager.set_font("unifont.ttf")
        self.manager.current = "title"

    def launch_popup(self):
        show = CreatePop()
        self.popupWindow = Popup(title="Create Mini Lesson", content=show,
                                 size_hint=(1, 0.7), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self)
        # open popup window
        self.popupWindow.open()

    def set_previous_screen(self):
        if self.manager.current == 'lessons':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def launch_del_popup(self):
        self.popup_delete = DeletePop()
        self.popup_delete.set_screen_instance(self,self.manager.get_screen('groups').selected_group)

        self.popup_delete.open()


class ImportPop(BoxLayout):
    text_userid = StringProperty()
    text_classid = StringProperty()
    text_lessonid = StringProperty()
    text_status = StringProperty()
    lesson_groups = ListProperty()
    selected_group = StringProperty("Group A")

    def __init__(self, **kwargs):

        super(ImportPop, self).__init__(**kwargs)
        self.lesson_import_flag = 0

    def import_lesson(self,button_sub):

        button_sub.state = "down"
        print(self.text_classid+self.text_userid+self.text_lessonid)
        response_code = 0
        if self.lesson_import_flag == 0:
             response_code, json_object = data_lessons.import_new_lesson(self.text_userid,self.text_classid,self.text_lessonid)

        if response_code == 1:
            self.text_status = "There was an error accessing the lesson. Check your access details."
            button_sub.disabled = False
            button_sub.state = "normal"
            self.lesson_import_flag = 0
        else:

            self.text_status = "Access details correct. Downloading the lesson..."
            self.call_update = Thread(target = data_lessons.update_lesson_details,args=(json_object,))
            self.call_update.start()
            self.progress_bar = ProgressBar()
            self.popup = Popup(
                title='Importing lesson',
                content=self.progress_bar,
                size_hint=(1, 0.3), auto_dismiss=False
            )
            self.popup.open()
            Clock.schedule_interval(self.next, 0.5)





    def next(self, dt):
        groupid = ""
        if self.call_update.is_alive():
            self.progress_bar.value += 5
        else:
            if self.selected_group == "Group A":
                groupid = 1
            elif self.selected_group == "Group B":
                groupid = 2
            elif self.selected_group == "Group C":
                groupid = 3
            elif self.selected_group == "Group D":
                groupid = 4
            elif self.selected_group == "Group E":
                groupid = 5

            data_capture_lessons.update_group_id(groupid)
            self.popup.dismiss()
            self.lesson_import_flag = 0
            self.text_status ="Import Completed and the Lesson is added to the "+self.selected_group
            return False


    def close_pop(self):

        self.popw.dismiss()

    def set_popupw(self,pop):
        self.popw=pop

    def set_screen_instance(self,listscreen,lessongroups):
        self.listscreen =listscreen
        self.lesson_groups = lessongroups
        print(self.lesson_groups)

    def on_select_group(self, group):
        self.selected_group = group



class ScreenManagement(ScreenManager):
    lesson_dictionary = {}
    lesson_lang = ""
    lesson_font = StringProperty()
    def set_lang(self,text):
        self.lesson_lang = text
    def get_lang(self):
        return self.lesson_lang
    def set_font(self,text):
        self.lesson_font = text
    def get_font(self):
        return self.lesson_font


    pass


class CreatePop(BoxLayout):
    text_lesson_name = StringProperty()
    text_lesson_font = StringProperty("Caveat-Bold.ttf")
    lesson_groups = ListProperty()
    text_status = StringProperty()
    selected_group = StringProperty("Group A")

    def __init__(self, **kwargs):
        super(CreatePop, self).__init__(**kwargs)
        self.lang_lesson = "English"


    def create_lesson(self, *args):
        if hasattr(self,"lang_lesson") == False:
            self.lang_lesson = "English"


        data_capture_lessons.create_lesson(self.text_lesson_name,self.lang_lesson)
        self.lessonid = data_capture_lessons.get_new_id()
        if not os.path.exists("Lessons/Lesson" + str(self.lessonid)):
            os.mkdir("Lessons/Lesson" + str(self.lessonid))
            os.mkdir("Lessons/Lesson" + str(self.lessonid) + "/images")
        shutil.copyfile("placeholder.png", "Lessons/Lesson" + str(self.lessonid) + "/images/placeholder.png")
        groupid = ""
        if self.selected_group == "Group A":
            groupid = 1
        elif self.selected_group == "Group B":
            groupid = 2
        elif self.selected_group == "Group C":
            groupid = 3
        elif self.selected_group == "Group D":
            groupid = 4
        elif self.selected_group == "Group E":
            groupid = 5

        data_capture_lessons.update_group_id(groupid)
        self.text_status = "Lesson is added to the " + self.selected_group

    def on_select_lang(self,text):
        self.lang_lesson = text
        if text != "English":
            self.text_lesson_font = "unifont.ttf"

    def on_title_text(self,wid,text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lang_lesson != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+' '
            wid.text = output

    def close_pop(self, *args):

        self.popw.dismiss()

    def set_screen_instance(self, listscreen,lessongroups):
        self.listscreen = listscreen
        self.lesson_groups = lessongroups
        print(self.lesson_groups)

    def set_popupw(self, pop):
        self.popw = pop

    def on_select_group(self, group):
        self.selected_group = group

class lessonpurchasepopup(Popup):
    def lesson_purchase(self):
        webbrowser.open("https://thelearningroom.el.r.appspot.com/login")

class DeletePop(Popup):
    lesson_list = ListProperty()

    selected_lesson = StringProperty()
    status_label = StringProperty()

    def __init__(self, **kwargs):
        super(DeletePop, self).__init__(**kwargs)

    def fill_lesson_list(self):
        lessons = data_capture_lessons.get_Lessons_ofgroup(self.groupid)
        lessonlistdisplay = []
        for element in lessons:
            lesson_display = str(element[0]) + ":" + element[1]
            lessonlistdisplay.append(lesson_display)
        self.lesson_list = lessonlistdisplay

    def on_select_lesson(self, lesson):
        self.selected_lesson = lesson

    def on_delete(self):
        if self.selected_lesson != "Selected Lesson":
            lesson_id = self.selected_lesson.split(":")[0]
            deletion = data_lessons.delete_lesson(lesson_id)
            if deletion == 0:
                self.status_label = "You have deleted the selected lesson"
            else:
                self.status_label = "We could not delete the lesson, try again"
        self.listscreen.ids.lesson_c.clear_widgets()
        self.listscreen.add_buttons(1)

    def set_screen_instance(self, listscreen,groupid):
        self.listscreen = listscreen
        self.groupid = groupid
        self.fill_lesson_list()

class LessonTitleScreen(Screen):
    text_label_1 = StringProperty()
    text_label_2 = StringProperty()
    text_image = StringProperty()
    animation_count = NumericProperty()
    font_name = StringProperty("Caveat-Bold.ttf")

    def __init__(self, **kwargs):
        super(LessonTitleScreen, self).__init__(**kwargs)

        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'title':
                self.manager.current = 'lessons'
                return True

    def read_intro(self, sb_button):
        pass
    def on_title_text(self,wid,text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
           text = text.strip()
           output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
           output = output+" "
           wid.text = output
    def on_title_desc_text(self,wid,text):

        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
           text = text.strip()
           output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
           output = output+" "
           wid.text = output

    def reset_speak_flag(self, t):
        self.speak_flag = 0

    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        self.font_name = self.manager.get_font()
        title, title_image, title_running_notes = data_capture_lessons.get_title_info(self.lessonid)
        if title_running_notes is not None:
             self.text_label_1 = title_running_notes
            # text_to_check = "अंतरिक्ष"
             #self.text_label_1 = arabic_reshaper.reshape(text_to_check)
        else:
            self.text_label_1 = ""
        if title is not None:
            self.text_label_2 = title
        else:
            self.text_label_2 = ""
        if title_image is not None:
            #imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/" + title_image
            imagepath = "Lessons/Lesson" +str(self.lessonid)+ "/images/" + title_image
            if os.path.exists(imagepath) and title_image != "":
                self.text_image = imagepath
            else:

                self.text_image = "placeholder.png"
        else:

            self.text_image = "placeholder.png"



    def set_previous_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def set_next_screen(self):
        if self.manager.current == 'title':
            if self.text_label_1 is None:
                self.text_label_1 = ""
            if self.text_label_2 is None:
                self.text_label_2 = ""

            data_capture_lessons.save_changes(self.lessonid,ntpath.basename(self.text_image),self.text_label_2,self.text_label_1)
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def launch_image_selector(self):
        self.popup_imageselect = ImageSelectPop(self)

        self.popup_imageselect.open()



class ImageSelectPop(Popup):
    search_query = StringProperty()
    def __init__(self,parentscreen,screenindex=100,**kwargs):
        super().__init__(**kwargs)
        self.parentscreen = parentscreen
        self.image_index =screenindex



    def showImages(self):
        print("button pressed" + self.search_query)
        img_util = image_utils.ImageUtils()
        image_urls = img_util.search_images(self.search_query)
        self.ids.imagelist.clear_widgets()

        self.async_images = []
        self.button_images = []
        for image in image_urls:
            try:
                box_layout = BoxLayout(orientation='vertical')
                async_image = AsyncImage(source=image,nocache=True, size=(200, 200))
                self.async_images.append(async_image)
                button_image = Button(text="view", size_hint=(0.4, 0.2),background_color=[0.76,0.83,0.86,0.8], pos_hint={'center_x': .5, 'center_y': .5})
                button_image.on_release = lambda instance=button_image, a=image: self.load_image(instance, a)
                self.button_images.append(button_image)
                box_layout.add_widget(async_image)
                box_layout.add_widget(button_image)
                self.ids.imagelist.add_widget(box_layout)
            except:
                print("The cache exception caught")


    def load_image(self, source, src):
        img_pop = imgpopup()
        img_pop.set_text(src)
        img_pop.set_parentscreen(self.parentscreen,self.image_index, self)
        img_pop.open()
        print("image touched" + src)
    def file_select(self):

       pass

    def file_pop(self):
         img_pop = imgurlpopup()
         img_pop.set_parentscreen(self.parentscreen, self.image_index, self)
         img_pop.open()


class LimitedTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if len(self.text) < 45:  # if the length of the substring is less than 10, return the substring
            s = substring
        else:
            s = ""  # is the substring length is 10 or greater, only return the first 10 characters
        return super().insert_text(s, from_undo=from_undo)


class imgurlpopup(Popup):
    text_image = StringProperty("placeholder.png")

    def set_parentscreen(self, parent,image_index, pop):
        self.parentscreen = parent
        self.pop = pop
        self.image_index = image_index
    def show_image(self,text):
        self.text_image = text
    def file_resize(self,imagefile):
        import PIL
        size = os.path.getsize(imagefile)
        i_type = imghdr.what(imagefile)
        img = PIL.Image.open(imagefile)

        if size <= 500000:
            img.save("titletmp." + i_type)
            return ("titletmp." + i_type)
        else:
            w, h = img.size
            img = img.resize((int(w/2),int(h/2)))

            img.save("titletmp."+i_type)
            return(self.file_resize("titletmp."+i_type))

    def save_selected_image(self,*args):
        file_to_copy = args[1][0]
        print(args)

        if not os.path.exists("Lessons/Lesson" + str(self.parentscreen.lessonid)):
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid))
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid) + "/images")
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
            self.parentscreen.lessonid) + os.path.sep + "images" + os.path.sep

        file_name_resized = ""
        filename = ""
        try:


            file_name_resized = self.file_resize(file_to_copy)
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        try:
            filetype = imghdr.what(file_name_resized)
            print(filetype)
            if filetype != "png" and filetype != "gif" and filetype != "jpg" and filetype != "jpeg":
                print("wrong file type")
                return
            fname_base = ""
            if self.parentscreen.manager.current == 'title':
                fname_base = "title"
            elif self.parentscreen.manager.current == 'factual':
                fname_base = "term"+str(self.image_index)
            elif self.parentscreen.manager.current == 'apply':
                fname_base = "step" + str(self.image_index)

            if filetype is not None:
                filename = self.filename_pfix + fname_base+"." + filetype
            else:
                filename = self.filename_pfix + fname_base
            shutil.copyfile(file_name_resized, filename)
            os.remove(file_name_resized)
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        if self.parentscreen.manager.current == "title":
            self.parentscreen.text_image = filename
            self.parentscreen.ids.tl_image.reload()
        elif self.parentscreen.manager.current =="factual":
            self.parentscreen.text_image_display = filename
            self.parentscreen.ids.display_image.reload()
        elif self.parentscreen.manager.current == "apply":

            if self.image_index == 0:
                self.parentscreen.step_image_0.source = filename
                self.parentscreen.step_image_0.reload()
            elif self.image_index == 1:
                self.parentscreen.step_image_1.source = filename
                self.parentscreen.step_image_1.reload()
            elif self.image_index == 2:
                self.parentscreen.step_image_2.source = filename
                self.parentscreen.step_image_2.reload()
            elif self.image_index == 3:
                self.parentscreen.step_image_3.source = filename
                self.parentscreen.step_image_3.reload()
            elif self.image_index == 4:
                self.parentscreen.step_image_4.source = filename
                self.parentscreen.step_image_4.reload()
            elif self.image_index == 5:
                self.parentscreen.step_image_5.source = filename
                self.parentscreen.step_image_5.reload()
            elif self.image_index == 6:
                self.parentscreen.step_image_6.source = filename
                self.parentscreen.step_image_6.reload()
            elif self.image_index == 7:
                self.parentscreen.step_image_7.source = filename
                self.parentscreen.step_image_7.reload()

        self.dismiss()
        self.pop.dismiss()



class imgpopup(Popup):
    text_image = StringProperty()

    def set_text(self, text_image):
        self.text_image = text_image

    def set_parentscreen(self, parent,image_index, pop):
        self.parentscreen = parent
        self.pop = pop
        self.image_index = image_index

    def file_resize(self,imagefile):
        import PIL
        size = os.path.getsize(imagefile)
        i_type = imghdr.what(imagefile)
        img = PIL.Image.open(imagefile)

        if size <= 500000:
            if i_type is not None:
                img.save("titletmp." + i_type)
                return ("titletmp." + i_type)
            else:
                img.save("titletmp")
                return "titletmp"
        else:
            w, h = img.size
            img = img.resize((int(w/2),int(h/2)))

            img.save("titletmp."+i_type)
            return(self.file_resize("titletmp."+i_type))

    def save_selected_image(self):
        print(self.text_image)

        if not os.path.exists("Lessons/Lesson" + str(self.parentscreen.lessonid)):
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid))
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid) + "/images")
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
            self.parentscreen.lessonid) + os.path.sep + "images" + os.path.sep
        filename = ""
        file_name_resized = "titletmp"
        try:

            response = requests.get(self.text_image)
            if response.status_code == 400 or response.status_code == 500:
                return "error"
            file = open("titletmp", "wb")
            file.write(response.content)
            file.close()
            file_name_resized = self.file_resize("titletmp")
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        try:
            filetype = imghdr.what(file_name_resized)
            fname_base = ""
            if self.parentscreen.manager.current == 'title':
                fname_base = "title"
            elif self.parentscreen.manager.current == 'factual':
                fname_base = "term" + str(self.image_index)
            elif self.parentscreen.manager.current == 'apply':
                fname_base = "step" + str(self.image_index)

            if filetype is not None:
                filename = self.filename_pfix + fname_base + "." + filetype
            else:
                filename = self.filename_pfix + fname_base
            shutil.copyfile(file_name_resized, filename)
            os.remove(file_name_resized)
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        if self.parentscreen.manager.current == "title":
            self.parentscreen.text_image = filename
            self.parentscreen.ids.tl_image.reload()
        elif self.parentscreen.manager.current =="factual":
            self.parentscreen.text_image_display = filename
            self.parentscreen.ids.display_image.reload()
        elif self.parentscreen.manager.current == "apply":

            if self.image_index == 0:
                self.parentscreen.step_image_0.source = filename
                self.parentscreen.step_image_0.reload()
            elif self.image_index == 1:
                self.parentscreen.step_image_1.source = filename
                self.parentscreen.step_image_1.reload()
            elif self.image_index == 2:
                self.parentscreen.step_image_2.source = filename
                self.parentscreen.step_image_2.reload()
            elif self.image_index == 3:
                self.parentscreen.step_image_3.source = filename
                self.parentscreen.step_image_3.reload()
            elif self.image_index == 4:
                self.parentscreen.step_image_4.source = filename
                self.parentscreen.step_image_4.reload()
            elif self.image_index == 5:
                self.parentscreen.step_image_5.source = filename
                self.parentscreen.step_image_5.reload()
            elif self.image_index == 6:
                self.parentscreen.step_image_6.source = filename
                self.parentscreen.step_image_6.reload()
            elif self.image_index == 7:
                self.parentscreen.step_image_7.source = filename
                self.parentscreen.step_image_7.reload()

        self.dismiss()
        self.pop.dismiss()
        

class LessonFactualScreen(Screen):
    text_image_1 = StringProperty()
    text_image_2 = StringProperty()
    text_image_3 = StringProperty()
    text_image_display = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")

    text_term_description_1 = StringProperty()
    text_term_description_2 = StringProperty()
    text_term_description_3 = StringProperty()
    text_term_description = StringProperty()
    text_term_display = StringProperty()

    def on_term_text(self, wid, text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+" "
            wid.text = output

    def on_description_text(self, wid, text):

        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+" "
            wid.text = output
    def __init__(self, **kwargs):
        super(LessonFactualScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        self.font_name = self.manager.get_font()
        self.display_index = 0
        self.draw_Screen()
        self.text_image_display = self.text_image_1
        self.text_term_description = self.text_term_description_1
        self.text_term_display = self.text_term_display_1
    def draw_Screen(self):
        self.textimage_1,  self.textimage_2,  self.textimage_3 = data_capture_lessons.get_fact_images(self.lessonid)
        self.text_term_1,  self.text_term_2,  self.text_term_3 = data_capture_lessons.get_fact_terms(self.lessonid)
        self.textterm_description_1,  self.textterm_description_2,  self.textterm_description_3 = data_capture_lessons.get_fact_descriptions(
            self.lessonid)
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        if  self.textimage_1 is None:
            self.textimage_1 = ""
        if  self.textimage_2 is None:
            self.textimage_2 = ""
        if  self.textimage_3 is None:
            self.textimage_3 = ""
        text_image1 = imagepath +  self.textimage_1
        text_image2 = imagepath +  self.textimage_2
        text_image3 = imagepath +  self.textimage_3

        if  self.textterm_description_1 is not None:
            self.text_term_description_1 =  self.textterm_description_1
        else:
            self.text_term_description_1 = ""
        if  self.textterm_description_2 is not None:
            self.text_term_description_2 =  self.textterm_description_2
        else:
            self.text_term_description_2 = ""
        if  self.textterm_description_3 is not None:
            self.text_term_description_3 =  self.textterm_description_3
        else:
            self.text_term_description_3 = ""
        if  self.text_term_1 is not None:
            self.text_term_display_1 =  self.text_term_1
        else:
            self.text_term_display_1 = ""
        if  self.text_term_2 is not None:
            self.text_term_display_2 =  self.text_term_2
        else:
            self.text_term_display_2 = ""
        if  self.text_term_3 is not None:
            self.text_term_display_3 =  self.text_term_3
        else:
            self.text_term_display_3 = ""

        if not os.path.exists(text_image1) or  self.textimage_1 == "":
            self.text_image_1 = "placeholder.png"
        else:
            self.text_image_1 = text_image1
        if not os.path.exists(text_image2) or  self.textimage_2 == "":
            self.text_image_2 = "placeholder.png"
        else:
            self.text_image_2 = text_image2
        if not os.path.exists(text_image3) or  self.textimage_3 == "":
            self.text_image_3 = "placeholder.png"
        else:
            self.text_image_3 = text_image3



    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'factual':
                self.manager.transition.direction = 'right'
                self.manager.current = 'title'
                return True



    def load_next(self):
        if self.text_term_display is None:
            self.text_term_display = ""
        if self.text_term_description is None:
            self.text_term_description = ""

        if self.display_index == 3:
            self.display_index = 0

        if self.display_index == 0:
            data_capture_lessons.update_term1(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description, self.text_term_display)
            # self.text_image_display = self.text_image_1
            # self.text_term_description = self.text_term_description_1
            # self.text_term_display = self.text_term_display_1
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
            self.text_term_display = self.text_term_display_2

        elif self.display_index == 1:
            data_capture_lessons.update_term2(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)
            # self.text_image_display = self.text_image_2
            # self.text_term_description = self.text_term_description_2
            # self.text_term_display = self.text_term_display_2
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3
            self.text_term_display = self.text_term_display_3

        else:
            data_capture_lessons.update_term3(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)
            # self.text_image_display = self.text_image_3
            # self.text_term_description = self.text_term_description_3
            # self.text_term_display = self.text_term_display_3
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
            self.text_term_display = self.text_term_display_1

        self.draw_Screen()
        self.display_index += 1
    def load_previous(self):

        self.display_index -= 1
        if self.display_index == -1:
            self.display_index = 2

        if self.display_index == 0:
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
            self.text_term_display = self.text_term_display_1
        elif self.display_index == 1:
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
            self.text_term_display = self.text_term_display_2
        else:
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3
            self.text_term_display = self.text_term_display_3

    def set_previous_screen(self):
        if self.manager.current == 'factual':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def set_next_screen(self):
        if self.manager.current == 'factual':
            self.update_current_values()
            self.update_empty_values()
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()
    def launch_image_selector(self):
        self.popup_imageselect = ImageSelectPop(self,self.display_index)

        self.popup_imageselect.open()

    def update_current_values(self):
        if self.text_term_display is None:
            self.text_term_display = ""
        if self.text_term_description is None:
            self.text_term_description = ""

        if self.display_index == 0:
            data_capture_lessons.update_term1(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description, self.text_term_display)

        elif self.display_index == 1:
            data_capture_lessons.update_term2(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)


        elif self.display_index == 2:
            data_capture_lessons.update_term3(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)

    def update_empty_values(self):
        self.textimage_1, self.textimage_2, self.textimage_3 = data_capture_lessons.get_fact_images(self.lessonid)
        self.text_term_1, self.text_term_2, self.text_term_3 = data_capture_lessons.get_fact_terms(self.lessonid)
        self.textterm_description_1, self.textterm_description_2, self.textterm_description_3 = data_capture_lessons.get_fact_descriptions(
            self.lessonid)
        if self.textimage_2 is None or self.textimage_2 == "":
            self.textimage_2 = "placeholder.png"
        if self.textimage_3 is None or self.textimage_3 == "":
            self.textimage_3 = "placeholder.png"
        if self.text_term_2 is None:
            self.text_term_2 = ""
        if self.text_term_3 is None:
            self.text_term_3 = ""
        if self.textterm_description_2 is None:
            self.textterm_description_2 = ""
        if self.textterm_description_3 is None:
            self.textterm_description_3 = ""


        data_capture_lessons.update_term2(self.lessonid, self.textimage_2,
                                          self.textterm_description_2,
                                          self.text_term_2)
        data_capture_lessons.update_term3(self.lessonid, self.textimage_3,
                                          self.textterm_description_3,
                                          self.text_term_3)

class LessonApplyScreen(Screen):
    text_label_1 = StringProperty("Dynamic Text" + str(random.randint(1, 100)))
    text_label_2 = StringProperty("test.png")
    font_name = StringProperty("Caveat-Bold.ttf")
    steps = ObjectProperty(None)
    text_image_0 = StringProperty()
    stepimage0 = ObjectProperty()

    def __init__(self, **kwargs):
        super(LessonApplyScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'apply':
                self.manager.transition.direction = 'right'
                self.manager.current = 'notes'
                return True

    def on_enter(self):

        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        self.font_name = self.manager.get_font()
        self.number_of_steps = data_capture_lessons.get_number_of_steps(self.lessonid)
        self.step_list = data_capture_lessons.get_description_list(self.lessonid)
        self.image_list = data_capture_lessons.get_step_image_list(self.lessonid)
        if self.number_of_steps is None:
            self.number_of_steps = 1
        self.add_steps_buttons()

    def set_previous_screen(self):
        if self.manager.current == 'apply':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()
    def save_screen(self):

        data_capture_lessons.save_step_texts(self.lessonid,self.text_input_0.text,self.text_input_1.text,self.text_input_2.text,self.text_input_3.text,self.text_input_4.text,self.text_input_5.text,
                                             self.text_input_6.text,self.text_input_7.text)
        data_capture_lessons.save_step_images(self.lessonid,ntpath.basename(self.step_image_0.source),ntpath.basename(self.step_image_1.source),ntpath.basename(self.step_image_2.source),
                                             ntpath.basename(self.step_image_3.source),ntpath.basename(self.step_image_4.source),ntpath.basename(self.step_image_5.source),
                                             ntpath.basename(self.step_image_6.source), ntpath.basename(self.step_image_7.source))

    def set_next_screen(self):
        if self.manager.current == 'apply':
            self.save_screen()
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def on_description_text(self, wid, text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+' '
            wid.text = output
    def add_steps_buttons(self):
        self.steps.clear_widgets()
        self.ids.steps.bind(minimum_height=self.ids.steps.setter('height'))
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        for i in range(8):
            text = self.step_list[i]
            if text is None:
                text = ""
            self.bx_layout = BoxLayout(spacing = [20,10])
            if i == 0:
                self.text_input_0 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_0.bind(text = lambda instance=self.text_input_0, text=self.text_input_0.text:self.on_description_text(instance,text))
                self.bx_layout.add_widget(self.text_input_0)
            elif i == 1:
                self.text_input_1 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_1.bind(text = lambda instance=self.text_input_1,text=self.text_input_1.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_1)
            elif i == 2:
                self.text_input_2 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})


                self.text_input_2.bind(text = lambda instance=self.text_input_2, text=self.text_input_2.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_2)
            elif i == 3:
                self.text_input_3 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False, font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_3.bind( text = lambda instance=self.text_input_3,text=self.text_input_3.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_3)
            elif i == 4:
                self.text_input_4 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_4.bind(text = lambda instance=self.text_input_4,text=self.text_input_4.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_4)
            elif i == 5:
                self.text_input_5 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_5.bind(text = lambda instance=self.text_input_5,text=self.text_input_5.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_5)
            elif i == 6:
                self.text_input_6 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_6.bind(text =  lambda instance=self.text_input_6,text=self.text_input_6.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_6)
            elif i == 7:
                self.text_input_7 = LimitedTextInput(text=text, height="80sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='50sp',write_tab = False,font_name=self.font_name,pos_hint={'center_y':0.5})
                self.text_input_7.bind(text =  lambda instance=self.text_input_7,text=self.text_input_7.text: self.on_description_text(instance, text))
                self.bx_layout.add_widget(self.text_input_7)

            image_button = Button(text="Image",background_color=[0.76,0.83,0.86,0.8],size_hint = (0.1,0.2),pos_hint={'center_y':0.5})
            image_button.on_release=lambda instance = image_button,a=i:self.image_select(instance,a)


            self.bx_layout.add_widget(image_button)

            if i == 0 :
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_0 = "placeholder.png"
                else:
                    self.text_image_0 = imagepath + self.image_list[i]
                self.step_image_0 = Image(source=self.text_image_0, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_0)
            elif i == 1 :
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_1 = "placeholder.png"
                else:
                    self.text_image_1 = imagepath + self.image_list[i]
                self.step_image_1 = Image(source=self.text_image_1,  size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_1)
            elif i == 2:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_2 = "placeholder.png"
                else:
                    self.text_image_2 = imagepath + self.image_list[i]
                self.step_image_2 = Image(source=self.text_image_2, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_2)
            elif i == 3:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_3 = "placeholder.png"
                else:
                    self.text_image_3 = imagepath + self.image_list[i]
                self.step_image_3 = Image(source=self.text_image_3, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_3)
            elif i == 4:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_4 = "placeholder.png"
                else:
                    self.text_image_4 = imagepath + self.image_list[i]
                self.step_image_4 = Image(source=self.text_image_4, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_4)
            elif i == 5:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_5 = "placeholder.png"
                else:
                    self.text_image_5 = imagepath + self.image_list[i]
                self.step_image_5 = Image(source=self.text_image_5, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_5)
            elif i == 6:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_6 = "placeholder.png"
                else:
                    self.text_image_6 = imagepath + self.image_list[i]
                self.step_image_6  = Image(source=self.text_image_6, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_6)
            elif i == 7:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_7 = "placeholder.png"
                else:
                    self.text_image_7 = imagepath + self.image_list[i]
                self.step_image_7 = Image(source=self.text_image_7, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_7)


           # button.on_release = lambda instance=button, a=i: self.add_image(instance, a)
            self.steps.add_widget(self.bx_layout)

    def image_select(self,instance,display_index,*args):
        self.popup_imageselect = ImageSelectPop(self,display_index)
        self.popup_imageselect.open()



class CWidget(Widget):
    pencolor = ListProperty([0, 1, 1, 1])
    line_width = 3
    text_button = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.text_button = "erase"
        self.start_flag = False
    def set_font(self,text):
        self.font_name = text

    def set_language(self, text):
        self.lesson_language = text

    def show_text(self,*args):
        self.tlabel = Label(text=self.input_text.text,pos=self.location,font_size='50sp',font_name=self.font_name,color=[1,0,0,0.9])
        self.add_widget(self.tlabel)

        self.popup.dismiss()

    def on_description_text(self, wid, text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+' '
            wid.text = output
    def on_touch_down(self, touch):

        if touch.is_double_tap:
            print("double tap")
            self.location = (touch.x,touch.y)
            self.blayout = BoxLayout()
            self.input_text = TextInput(font_name=self.font_name,font_size="50sp",multiline=False)
            self.input_text.bind(text = lambda instance=self.input_text,text=self.input_text.text: self.on_description_text(instance, text))
            self.input_button = Button(text="Add Text",on_release=self.show_text)
            self.blayout.add_widget(self.input_text)
            self.blayout.add_widget(self.input_button)

            self.popup = Popup(
                title='Enter Text',
                content = self.blayout,
                size_hint=(1, 0.2), auto_dismiss=False
            )
            self.popup.open()
        with self.canvas:
            Color(rgba = self.pencolor)
            self.start_flag= True
            touch.ud['line'] = Line(points=(touch.x, touch.y),width=self.line_width)

            #d = 70
            #Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
    def erase(self):
        self.pencolor = [0,0,0,1]
        self.line_width = 15
    def pen(self):
        self.pencolor = [0,1,1,1]
        self.line_width = 3
    def clear(self):
        self.canvas.clear()
        print("clear")

    def on_touch_move(self, touch):
        if hasattr(touch, "ud") and self.start_flag:
            touch.ud['line'].points += [touch.x, touch.y]


class LessonWhiteboardScreen(Screen):
    def __init__(self,**kwargs):
        super(LessonWhiteboardScreen,self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_enter(self):
        self.ids.cw.set_font(self.manager.get_font())
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        self.ids.cw.set_language(self.lesson_language)
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
            self.lessonid) + os.path.sep + "images" + os.path.sep

    def open_last_saved(self):
        img_wb_pop = imgwhiteboardpopup()
        whiteboard_path = "Lessons" + os.path.sep + "Lesson" + str(self.lessonid) + os.path.sep + "images" + os.path.sep+"whiteboard.png"
        if (os.path.exists(whiteboard_path)):
            img_wb_pop.set_image_file("Last Saved Board",whiteboard_path)
            img_wb_pop.ids.img_wb.reload()

        img_wb_pop.open()


    def save_canvas(self,sv):
        self.sten_view= sv

        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        sv.export_to_png(self.filename_pfix+os.path.sep+"whiteboard.png")
        exists = os.path.exists(self.filename_pfix+os.path.sep+"whiteboard.png")


        print("Exists Check "+str(exists))



        data_capture_lessons.save_whiteboard_image(self.lessonid,"whiteboard.png")

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'whiteboard':
                self.manager.current = 'factual'
                self.manager.transition.direction = 'right'
                return True


    def set_next_screen(self):
        if self.manager.current == 'whiteboard':
            #   self.save_canvas(self.ids.sv)
            if os.path.exists(self.filename_pfix+"whiteboard.png") == False:
                data_capture_lessons.save_whiteboard_image(self.lessonid, "")
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def set_previous_screen(self):
        if self.manager.current == 'whiteboard':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()



class imgwhiteboardpopup(Popup):
    text_image_presence = StringProperty("No Save Board Yet")
    whiteboard_image = StringProperty("trans.png")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_image_file(self,presence,filename):
        self.text_image_presence = presence
        self.whiteboard_image = filename

class LessonNotesScreen(Screen):
    text_label_1 = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")

    def __init__(self, **kwargs):
        super(LessonNotesScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)


    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'notes':
                self.manager.transition.direction = 'right'
                self.manager.current = 'whiteboard'
                return True

    def on_description_text(self, wid, text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+' '
            wid.text = output

    def on_enter(self):
        self.font_name = self.manager.get_font()
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        txt_notes = data_capture_lessons.get_notes(self.lessonid)
        if (txt_notes is None):
            self.text_label_1 = ""
        else:
            self.text_label_1 = txt_notes

    def on_save(self):
        if self.text_label_1 is None:
            self.text_label_1 = ""
        ret = data_capture_lessons.save_notes(self.lessonid, self.text_label_1)
        print(self.text_label_1)
        print(str(ret))



    def set_next_screen(self):
        self.on_save()
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'left'
            self.manager.current = 'apply'

    def set_previous_screen(self):
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'right'
            self.manager.current = 'whiteboard'

class PublishPop(Popup):
    text_status = StringProperty("The lesson will be published in our servers with an access code.\n Students can access the lesson"
                                 " and get it into their devices from the \"Learning Room\" app -> https://play.google.com/store/apps/details?id=in.wondersky.lr")
    text_user = StringProperty()
    text_pwd = StringProperty()


    def set_screen_instance(self, parentscreen):
        self.parentscreen = parentscreen

        if data_capture_lessons.is_shared(self.parentscreen.lessonid):
            classid, userid = data_capture_lessons.get_user_classid()
            user_id = data_capture_lessons.get_userid(self.parentscreen.lessonid)
            self.text_status = "The lesson has been shared with following details\n User ID: " + str(user_id)+ " Class ID: " + str(classid)+ " Lesson ID: " + str(self.parentscreen.lessonid)
    def response_status(self,text):
        self.text_status = text
    def publish_lesson(self):
        self.logintoken = self.get_token(self.text_user, self.text_pwd)
        if self.logintoken == "Login_Failed":
            self.text_status = "Login Credentials could be wrong or check your connectivity"
        else:
            data = data_lessons.prepare_lesson_share(self.parentscreen.lessonid)
            self.call_update = Thread(target=data_lessons.post_lesson,
                                      args=(self,data, self.logintoken, self.parentscreen.lessonid))

            #response_text = data_lessons.post_lesson(data, self.logintoken, self.parentscreen.lessonid)
            # self.call_update = Thread(target=data_lessons.post_lesson, args=(data,self.logintoken,self.parentscreen.lessonid))
            self.call_update.start()
            self.progress_bar = ProgressBar()
            self.popup = Popup(
                title='Sharing lesson',
                content=self.progress_bar,
                size_hint=(1, 0.3), auto_dismiss=False
            )
            self.popup.open()
            Clock.schedule_interval(self.next, 0.5)




    def next(self, dt):
        if self.call_update.is_alive():
            self.progress_bar.value += 5
        else:
            self.popup.dismiss()
            c_check = "maximum"
            if (c_check in self.text_status):
                self.purchase_pop = lessonpurchasepopup()
                self.purchase_pop.open()
            return False

    def get_token(self, user, pwd):
        logintoken = data_lessons.get_token(user, pwd)
        return logintoken


    def register_user(self):
        webbrowser.open("https://thelearningroom.el.r.appspot.com/")


class LessonAssessScreen(Screen):
    text_label_1 = StringProperty()
    text_label_2 = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")


    def __init__(self, **kwargs):
        super(LessonAssessScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)


    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'assess':
                self.manager.transition.direction = 'right'
                self.manager.current = 'apply'
                return True

    def publish_lesson(self):
        self.on_save()
        self.popup_publish = PublishPop()
        self.popup_publish.set_screen_instance(self)

        self.popup_publish.open()

    def on_description_text(self, wid, text):
        if text is not None and len(text) > 0 and text[-1] == " " and self.lesson_language != "English":
            text = text.strip()
            output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            output = output+' '
            wid.text = output

    def on_enter(self):
        self.font_name = self.manager.get_font()
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.lesson_language = data_capture_lessons.get_lesson_lanugage(self.lessonid)
        txt_questions, txt_answers = data_capture_lessons.get_questions_answer(self.lessonid)
        if (txt_questions is None):
            self.text_label_1 = ""
        else:
            self.text_label_1 = txt_questions
        txt_form = data_capture_lessons.get_formlink(self.lessonid)
        if (txt_form is None):
            self.text_label_2 = ""
        else:
            self.text_label_2 = txt_form

    def on_save(self):
        if self.text_label_1 is None:
            self.text_label_1 = ""
        if self.text_label_2 is None:
            self.text_label_2 = ""

        ret = data_capture_lessons.set_questions(self.lessonid, self.text_label_1)
        ret1 = data_capture_lessons.set_form_link(self.lessonid, self.text_label_2)
        print(self.text_label_1)
        print(str(ret))

    def set_next_screen(self):
        self.on_save()
        if self.manager.current == 'assess':
            self.manager.transition.direction = 'left'
            self.manager.current = 'groups'

    def set_previous_screen(self):
        if self.manager.current == 'assess':
            self.manager.transition.direction = 'right'
            self.manager.current = 'apply'


class MagicTeacherApp(App):
    def on_pause(self):
        return True

    def build(self):
        self.icon = 'logo_bg_small.png'
        self.title = 'Lesson Creator'
        classid = data_capture_lessons.get_classid()
        if classid is None or classid == "":
            data_capture_lessons.set_classid()
        return ScreenManagement()



MagicTeacherApp().run()
