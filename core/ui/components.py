from typing import Callable
from tkinter import Event
import customtkinter as tk


class FramedLabel(tk.CTkFrame):
    
    def __init__(
        self,
        master,
        text: str,
        justify=tk.LEFT,
        anchor=tk.W,
        **kwargs
    ) -> None:
        super().__init__(master, **kwargs)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.label = tk.CTkLabel(
            self, text=text, justify=justify, anchor=anchor
        )
        self.label.grid(row=0, column=0, padx=10, sticky=tk.NSEW)
    
    def configure(self, *args, **kwargs) -> None:
        self.label.configure(*args, **kwargs)
    
    def cget(self, *args, **kwargs) -> None:
        try:
            return self.label.cget(*args, **kwargs)
        except AttributeError:
            return super().cget(*args, **kwargs)


class CachedText(tk.CTkTextbox):
    
    def __init__(self, *args, **kwargs) -> None:
        """A Text widget that caches the text and only calls the modified event when the text is changed."""
        self.text_cache = ""
        super().__init__(*args, **kwargs)
        self.on_changed_callbacks = []
        self.bind("<<Modified>>", self._on_text_changed)
    
    def add_on_changed_callback(
        self, func: Callable[[Event, str], None]
    ) -> None:
        self.on_changed_callbacks.append(func)
    
    def remove_on_changed_callback(
        self, func: Callable[[Event, str], None]
    ) -> None:
        self.on_changed_callbacks.remove(func)
    
    def _on_text_changed(self, event: Event) -> None:
        """
        NOTE: this is called twice when the text is changed. 
        This is not handled. Be aware of this.
        At the end of this function, the modified flag must be reset.
        Otherwise, the event will not be called again.
        """
        curr_text = self.get_text()
        
        if curr_text != self.text_cache:
            # does not seem to work
            self.event_generate("<<TextChanged>>")
            # thus, call our probprietary subscribers' functions
            for subscriber in self.on_changed_callbacks:
                try:
                    subscriber(event, curr_text)
                except Exception: #pylint: disable=broad-except
                    pass
        
        self.text_cache = curr_text
        # reset the modified flag
        # if this is not done, the modified event will not be called again
        event.widget.edit_modified(False)
    
    def get_text(self) -> str:
        txt = self.get(1.0, tk.END)
        # remove the last newline, which tkinter seems to add automatically
        if txt.endswith("\n"):
            txt = txt[:-1]
        return txt
    
    def get_text_from_cache(self) -> str:
        return self.text_cache
    
    def insert(self, *args, **kwargs) -> str:
        super().insert(*args, **kwargs)
        self.text_cache = self.get_text()
        return self.text_cache
    
    def clear(self) -> None:
        super().delete(1.0, tk.END)
        self.text_cache = self.get_text()
    
    def set_text(self, text) -> str:
        self.clear()
        self.insert(tk.END, text)
        self.text_cache = self.get_text()
        return self.text_cache
    
    def append_text(self, text, add_space=True) -> str:
        if add_space:
            self.insert(tk.END, " ")
        self.insert(tk.END, text)
        self.text_cache = self.get_text()
        return self.text_cache
