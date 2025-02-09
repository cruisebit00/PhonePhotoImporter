# https://www.youtube.com/watch?v=mop6g-c5HEY
# Last stop: 17:31:57

import customtkinter as ctk
import darkdetect
from settings import *

class PhotoImporterGUI(ctk.CTk):
    def __init__(self):

        # setup
        # https://youtu.be/mop6g-c5HEY?t=50030
        self.is_dark = darkdetect.isDark()
        super().__init__(fg_color=(WHITE, BLACK))
        ctk.set_appearance_mode(f'{'dark' if self.is_dark else 'light'}')
        self.geometry(f'1000x400')
        self.resizable(False, False)
        self.title("Photo importer")
        self.iconbitmap('PhotoImporterIcon.ico')

        # layout
        # https://youtu.be/mop6g-c5HEY?t=50389
        self.rowconfigure((0,1), weight = 1, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=4, uniform='a')

        # https://youtu.be/mop6g-c5HEY?t=50554

        self.mainloop()

def main():
    PhotoImporterGUI()
     
if __name__ == "__main__":
    main()