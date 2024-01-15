import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
import tempfile

root = tk.Tk()
frame = HtmlFrame(root, messages_enabled=False)

with open('documentation/documentation.md', 'r') as f:
    m_text = f.read()
m_html = markdown.markdown(m_text)
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write(m_html)
    f.close()
frame.load_file(f.name)
frame.pack(fill="both", expand=True)
root.mainloop()