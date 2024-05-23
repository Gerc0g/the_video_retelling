import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.Transcriber import Transcriber
from app.RetellingRequest import OpenAIChat
from app.VideoDecoder import VideoToAudioConverter
import os

class AudioSummarizerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Транскрибатор")

        self.videoDecoder = VideoToAudioConverter()
        self.transcriber = None
        self.retelling = None

        self.create_widgets()



    def create_widgets(self):

        self.model_label = ttk.Label(self.root, text="Выберите метод транскрибирования:")
        self.model_label.grid(row=1, column=0, sticky="e")
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(self.root, textvariable=self.model_var)
        self.model_combobox['values'] = ('tiny', 'base', 'small', 'medium', 'large')
        self.model_combobox.current(1)
        self.model_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.key_label = ttk.Label(self.root, text="Введите GPT API ключ:")
        self.key_label.grid(row=2, column=0, sticky="e")
        self.key_entry = ttk.Entry(self.root, show="*")
        self.key_entry.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.choose_button = ttk.Button(self.root, text="Выбрать файл(mp3 mp4)", command=self.choose_file)
        self.choose_button.grid(row=0, column=0, columnspan=2, pady=10)

        self.original_text_label = ttk.Label(self.root, text="Транскрибация Видео или Аудио файла:")
        self.original_text_label.grid(row=3, column=0, sticky="nsew")
        self.original_text = tk.Text(self.root, height=20, width=100)
        self.original_text.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.summary_text_label = ttk.Label(self.root, text="Краткий пересказ через LLM:")
        self.summary_text_label.grid(row=3, column=1, sticky="nsew")
        self.summary_text = tk.Text(self.root, height=20, width=100)
        self.summary_text.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")

        self.original_text_info_label = ttk.Label(self.root, text="info transcr:")
        self.original_text_info_label.grid(row=5, column=0, sticky="nsew")
        self.original_text_info = tk.Text(self.root, height=10, width=25)
        self.original_text_info.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

        self.summary_text_info_label = ttk.Label(self.root, text="info summary:")
        self.summary_text_info_label.grid(row=5, column=1, sticky="nsew")
        self.summary_text_info = tk.Text(self.root, height=10, width=25)
        self.summary_text_info.grid(row=6, column=1, padx=10, pady=10, sticky="nsew")


    def choose_file(self):
        gpt_key = self.key_entry.get().strip()
        model_size = self.model_var.get()

        if not gpt_key:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите GPT API ключ.")
            return

        self.retelling = OpenAIChat(api_key=gpt_key)
        self.transcriber = Transcriber(model_size=model_size)


        file_path = filedialog.askopenfilename(filetypes=[("Audio/Video Files", "*.mp3 *.mp4")])

        if file_path:
            self.process_summize(file_path)


    def process_summize(self, path):
        model_size = self.model_var.get()
        save_file_path = f"Data/Results/Summary {os.path.splitext(os.path.basename(path))[0]}.txt"

        try:
            if path.endswith(".mp3"):
                video_json = None
                transcribe_json = self.transcriber.transcribe(path)
            elif path.endswith(".mp4"):
                video_json = self.videoDecoder.extract_audio(path)
                transcribe_json = self.transcriber.transcribe(video_json['path'])
            else:
                messagebox.showwarning("Предупреждение", "Не верный формат файла. Приложение поддерживает только mp3 или mp4.")
                return


            text = transcribe_json['text']
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(tk.END, text)

            if video_json:
                text_info = f'Процесс - {str(transcribe_json["type"])}.\n\nМетод транскрибации - {model_size}.\n\nОпределил язык - {transcribe_json["lang"]}.'
                text_info += f'\n\nВремя [Видео->Аудио] - {video_json["timeout"]}.\n\nВремя [Аудио->Текст] - {transcribe_json["timeout"]}'

            else:
                text_info = f'Процесс - {str(transcribe_json["type"])}.\n\nМетод транскрибации - {model_size}.\n\nОпределил язык - {transcribe_json["lang"]}.\n\nВремя выполнения - {transcribe_json["timeout"]}'

            self.original_text_info.delete(1.0, tk.END)
            self.original_text_info.insert(tk.END, text_info)

            summary_json = self.retelling.summarize_text(text=text)

            summary_text = summary_json['text']
            with open(save_file_path, "w", encoding="utf-8") as file:
                file.write(summary_text)

            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary_text)

            summary_text_info = f'Время выполнения - {summary_json["timeout"]}.\n\nФайл с пересказом сохранен в - {save_file_path}.'
            self.summary_text_info.delete(1.0, tk.END)
            self.summary_text_info.insert(tk.END, summary_text_info)


        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = AudioSummarizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()