#  Copyright 2020 Swannet, Kilian

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import re
import tkinter as tk
from tkinter.filedialog import askopenfilename
from os.path import isfile
import codecs


class gui(tk.Tk):

    def __init__(self):
        super().__init__()
        # * variables
        self.file_path = tk.StringVar()
        self.status = tk.StringVar()
        self.status.set(' ')


        # * window setup
        self.title("X52PRO -> X52 profile converter")
        self.minsize(550, 150)
        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.rowconfigure(self, 3, weight=1)
        self.make_labels()
        self.make_entries()
        self.make_buttons()

    # ****************** LABELS ******************
    def make_labels(self):
        self.file_label = tk.Label(self, text="X52 PRO file:").grid(row=0,
                                                                  column=0,
                                                                  padx=10,
                                                                  sticky=tk.E)
        self.status_label = tk.Label(self, text="Status:").grid(row=2,
                                                                column=0,
                                                                padx=10,
                                                                sticky=tk.E)
        self.done_label = tk.Label(self, textvariable=self.status).grid(row=2,
                                                                column=1,
                                                                padx=10,
                                                                sticky=tk.W)


    # ****************** ENTRIES ******************
    def make_entries(self):
        self.FilePath_Frame = tk.Frame(self)
        self.FilePath_Frame.grid_columnconfigure(0, weight=1)
        self.FilePath_Frame.grid(row=0, column=1, padx=10, pady=15, sticky='nesw')
        self.file_entry = tk.Entry(self.FilePath_Frame,
                                   textvariable=self.file_path)
        self.file_entry.grid(row=0,
                             column=0,
                             padx=0,
                             pady=0,
                             sticky='ew')

        # * scrollbar
        self.path_scroll = tk.Scrollbar(self.FilePath_Frame,
                                        orient=tk.HORIZONTAL,
                                        command=self.file_entry.xview)
        self.path_scroll.grid(row=1,
                              column=0,
                              padx=0,
                              pady=0,
                              sticky=tk.E+tk.W+tk.N)
        self.file_entry.config(xscrollcommand=self.path_scroll.set)


    # ****************** BUTTONS ******************
    def make_buttons(self):
        self.quit_button = tk.Button(self,
                                     text="Quit",
                                     command=self.destroy,
                                     width=5).grid(row=3,
                                                   column=0,
                                                   padx=10,
                                                   pady=10,
                                                   sticky=tk.SW)
        self.ask_file_button = tk.Button(self,
                                         text="Browse files",
                                         command=self.open_file,
                                         width=10).grid(row=0,
                                                        column=2,
                                                        padx=10,
                                                        pady=10,
                                                        sticky='nesw')

        self.convert_button = tk.Button(self,
                                       text="Convert",
                                       command=self.run,
                                       width=10).grid(row=1,
                                                      column=2,
                                                      rowspan=3,
                                                      padx=10,
                                                      pady=10,
                                                      sticky='nesw')
        self.bind("<Return>", self.run)



    def run(self, event=None):
        self.status.set('started')
        if len(self.file_path.get()) == 0:
            self.status_label.set("! No file selected")
        elif not isfile(self.file_path.get()):
            self.status_label.set("! File not found")
        else:
            self.convert()

    def open_file(self):
        path = askopenfilename(#initialdir=r"C:\Users",
                               title="Select X52 PRO profile file (.pr0)",
                               filetypes=((("pr0 files"), ("*.pr0")),
                                          (("all files"), ("*.*"))))
        self.file_path.set(path)
        print(path)

        self.file_name = re.search(r'[^/]+(?=\.pr0$)', path).group(0)
        print(self.file_name)

    def convert(self):
        # path = r'C:/Users/Public/Documents/Logitech/X52/F-15C original.pr0'
        file_name = re.search(r'[^/]+(?=\.pr0$)', self.file_path.get()).group(0)
        new_file = file_name + "_converted.pr0"
        new_path = re.sub("{}{}".format(file_name, '.pr0'), new_file, self.file_path.get())


        encoded_text = open(self.file_path.get(), 'rb').read()  #read in binary mode to get the BOM correctly
        bom= codecs.BOM_UTF16_LE                                #print dir(codecs) for other encodings
        assert encoded_text.startswith(bom)                     #make sure the encoding is as expected
        # encoded_text= encoded_text[len(bom):]                 #strip away the BOM
        text= encoded_text.decode('utf-16le')

        text = re.sub(r"\[controller\=e81d998b.*?\]\]\]\]\]\]\]", "", text, 0, re.DOTALL)  # removing controller
        text = re.sub(r"\r\n\s*\r\n\s*", r"]\r\n", text)
        text = re.sub(r"\[controller\=1f732691-3bc6-41ec-a977-c5bf0b03a3dc group='Pro Flight'\r\n\s*\[member=75bb6cc8-fb40-4be1-bf2b-4b10397a98a8 name=X52Pro shortname=X52Pro\]",
                    r"[controller=e81d998b-c604-4d71-be97-35ca01439c7e group='Pro Flight'\r\n      [member=c7719f41-f667-4514-bbb4-3f38c9e4d05a name=X52 shortname=X52]",
                    text)
        text = re.sub(r"Launch", r"Fire", text)
        text = re.sub(r"Pinkie", r"'Pinkie Switch'", text)
        text = re.sub(r"\[button=0x00090006 name='Pinkie Switch']\r\n\s*\[button=0x00090007 name='Fire D']\r\n\s*\[button=0x00090008 name='Fire E']",
                    r"[button=0x00090007 name='Fire D']\r\n        [button=0x00090008 name='Fire E']\r\n        [button=0x00090006 name='Pinkie Switch']",
                    text)
        text = re.sub(r"0x0009001E", r"0x0009001A", text)
        text = re.sub(r"0x0009001F", r"0x0009001E", text)
        text = re.sub(r"0x00090010", r"0x0009001F", text)
        text = re.sub(r"0x00090013", r"0x00090020", text)

        text = re.sub(r"\[button=0x00090011 name='Wheel Scroll Up'\]\r\n\s*\[button=0x00090012 name='Wheel Scroll Down'\]",
                    r"[button=0x00090012 name='Wheel Scroll Down']\r\n        [button=0x00090011 name='Wheel Scroll Up']",
                    text)
        text = re.sub(r"0x00010033", r"tempval", text)
        text = re.sub(r"0x00010034", r"0x00010033", text)
        text = re.sub(r"tempval", r"0x00010034", text)

        text = re.sub(r"0x00090011", r"0x00090022", text)
        text = re.sub(r"0x00090012", r"0x00090021", text)
        text = re.sub(r"0x00090014", r"0x00090010", text)
        text = re.sub(r"'POV 2' way=5", r"'POV Hat 2' way=5", text)
        text = re.sub(r"0x00090018", r"0x00090014", text)
        text = re.sub(r"'Throttle Hat' way=5", r"'POV Hat 3' way=5", text)
        text = re.sub(r"\[slider name=Mode", r"[slider=0x00090018 name=Mode", text)
        text = re.sub(r"0x0009001C", r"0x00090018", text)
        text = re.sub(r"0x0009001D", r"0x00090019", text)
        text = re.sub(r"'POV 1' way=5", r"'POV Hat 1'", text)

        text = re.sub(r"\[axis=0x00010032 name=Throttle\]\r\n\s*\[axis=0x00010035 name=Twist\]",
                    r"[axis=0x00010035 name=Twist]\r\n        [axis=0x00010032 name=Throttle]",
                    text)
        text = re.sub(r"Twist", r"Rudder", text)
        text = re.sub(r"\[axis=0x00010034 name='Rotary 1'\]\r\n\s*\[axis=0x00010033 name='Rotary 2'\]",
                    r"[axis=0x00010033 name='Rotary 2']\r\n        [axis=0x00010034 name='Rotary 1']",
                    text)


        text = re.sub(r"Mouse X Axis", r"Ministick X Axis", text)
        text = re.sub(r"Mouse Y Axis", r"Ministick Y Axis", text)

        text = re.sub(r"cd957a00-26bf-4577-89ff-676166fe3b28 fallback=cd957a00-26bf-4577-89ff-676166fe3b28",
                    r"e8cb8c21-eb62-4268-8d2e-211c573bd12f fallback=e8cb8c21-eb62-4268-8d2e-211c573bd12f",
                    text)

        outfile = codecs.open(new_path, 'w+', encoding='utf-16-le')
        outfile.write(text)

        self.status.set('Done!\nFile created: {}\n\n Note that the driver software may cause the stick to disconnect if the profile file name contains numbers.\n To avoid this remove all numbers from the .pr0 filename!!!'.format(new_file))


if __name__ == "__main__":
    gui().mainloop()
