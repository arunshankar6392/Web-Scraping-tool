import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def set_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    return headers

def scrape_website_with_delay(url, loading_window):
    try:
        headers = set_headers()
        response = requests.get(url, headers=headers)
        time.sleep(2)  # Introduce a delay of 2 second to avoid chances of website crash 

        loading_window.destroy()
        return response.content
    except Exception as e:
        loading_window.destroy()
        messagebox.showerror(
            "Error", f"An error occurred while scraping the website:\n{e}")
        return None

def scrape_website_with_selenium(url, loading_window):
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # Waiting time to load dynamic content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))

        html_content = driver.page_source
        driver.quit()

        loading_window.destroy()
        return html_content
    except Exception as e:
        loading_window.destroy()
        messagebox.showerror(
            "Error", f"An error occurred while scraping the website:\n{e}")
        return None

def extract_information(html, tag):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all(tag)
        return [element.get_text().strip() for element in elements]
    except Exception as e:
        messagebox.showerror(
            "Error", f"An error occurred while extracting information:\n{e}")
        return []

def filter_relevant_data(tag_elements, keyword):
    try:
        relevant_data = [tag_element for tag_element in tag_elements if keyword.lower(
        ) in tag_element.lower()]
        return relevant_data
    except Exception as e:
        messagebox.showerror(
            "Error", f"An error occurred while filtering relevant data:\n{e}")
        return []

def clear_fields():
    try:
        url_entry.delete(0, tk.END)
        tag_entry.delete(0, tk.END)
        keyword_entry.delete(0, tk.END)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror(
            "Error", f"An error occurred while clearing fields:\n{e}")

def save_data():
    try:
        data = result_text.get(1.0, tk.END)
        if data:
            with open("scraped_data.txt", "w") as file:
                file.write(data)
            messagebox.showinfo("Saved", "Scraped data saved successfully!")
        else:
            messagebox.showwarning("No Data", "No data to save.")
    except Exception as e:
        messagebox.showerror(
            "Error", f"An error occurred while saving data:\n{e}")

def run_scraping():
    try:
        website_url = url_entry.get()

        loading_window = tk.Toplevel(window)
        loading_window.title("Loading...")
        loading_label = ttk.Label(
            loading_window, text="Scraping data, please wait...")
        loading_label.pack(padx=20, pady=10)
        loading_window.update()

        #Selenium used for handling dynamic content
        html_content = scrape_website_with_selenium(
            website_url, loading_window)

        if html_content:
            # If tag is provided, use it.Otherwise, extract all tags
            tag_name = tag_entry.get().lower()
            if tag_name:
                data = extract_information(html_content, tag_name)
                loading_window.destroy()

                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(
                    tk.END, f"\nExtracted Data for <{tag_name}>:\n")
                result_text.insert(
                    tk.END, "----------------------------------\n")
                result_text.insert(tk.END, "\n".join(data))

                # Filter function
                keyword = keyword_entry.get()
                relevant_data = filter_relevant_data(data, keyword)

                if relevant_data:
                    result_text.insert(
                        tk.END, f"\nRelevant data in <{tag_name}> containing '{keyword}':\n")
                    result_text.insert(
                        tk.END, "----------------------------------\n")
                    result_text.insert(tk.END, "\n".join(relevant_data))
                else:
                    result_text.insert(
                        tk.END, f"\nNo relevant data found in <{tag_name}> containing '{keyword}'.\n")

            else:
                # If tag is not provided, extract information from all tags
                soup = BeautifulSoup(html_content, 'html.parser')
                all_tags_data = [element.get_text().strip()
                                 for element in soup.find_all()]
                loading_window.destroy()

                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Extracted Data from all tags:\n")
                result_text.insert(
                    tk.END, "----------------------------------\n")
                result_text.insert(tk.END, "\n".join(all_tags_data))

                # Filter function
                keyword = keyword_entry.get()
                relevant_data = filter_relevant_data(all_tags_data, keyword)

                if relevant_data:
                    result_text.insert(
                        tk.END, f"\nRelevant data containing '{keyword}':\n")
                    result_text.insert(
                        tk.END, "----------------------------------\n")
                    result_text.insert(tk.END, "\n".join(relevant_data))
                else:
                    result_text.insert(
                        tk.END, f"\nNo relevant data found containing '{keyword}'.\n")

            result_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

window = tk.Tk()
window.title("Web Scraping GUI")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)

# Set window position
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Background image is downloaded and set
response = requests.get(
    "https://repository-images.githubusercontent.com/271454465/e453ad80-abde-11ea-93df-fe0442095c6d")
bg_image = Image.open(BytesIO(response.content))
bg_image = bg_image.resize((window_width, window_height))
background_image = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Style
style = ttk.Style()
style.configure('TButton', foreground='blue', font=(
    'Arial', 16, 'bold'))  # Larger and bold font for button
style.configure('TLabel', font=('Arial', 18))  # Larger font for labels
style.configure('TEntry', font=('Arial', 18))  # Larger font for entry fields

# URL Entry
url_label = ttk.Label(
    window, text="Enter the URL of the website:", style='TLabel')
url_label.grid(column=0, row=0, padx=10, pady=20)
url_entry = ttk.Entry(window, width=50)
url_entry.grid(column=1, row=0, padx=10, pady=10)

# Tag Entry
tag_label = ttk.Label(
    window, text="Enter the HTML tag name (e.g., div, p, span):", style='TLabel')
tag_label.grid(column=0, row=1, padx=10, pady=20)
tag_entry = ttk.Entry(window, width=25)
tag_entry.grid(column=1, row=1, padx=10, pady=10)

# Keyword Entry
keyword_label = ttk.Label(
    window, text="Enter a keyword for filtering:", style='TLabel')
keyword_label.grid(column=0, row=2, padx=10, pady=20)
keyword_entry = ttk.Entry(window, width=40)
keyword_entry.grid(column=1, row=2, padx=10, pady=10)

# Run Button
run_button = ttk.Button(
    window, text="Run", command=run_scraping, style='TButton')
# Increased pady between keyword entry and run button
run_button.grid(column=0, row=3, columnspan=2, pady=(50, 10))

# Clear Button
clear_button = ttk.Button(window, text="Clear",
                          command=clear_fields, style='TButton')
clear_button.grid(column=0, row=4, pady=(0, 10), padx=(10, 5), sticky=tk.W)

# Save Button
save_button = ttk.Button(
    window, text="Save", command=save_data, style='TButton')
save_button.grid(column=1, row=4, pady=(0, 10), padx=(5, 20), sticky=tk.W)

# Result Text
result_text = scrolledtext.ScrolledText(
    window, width=80, height=12, wrap=tk.WORD, state=tk.DISABLED, font=('Arial', 14))  # Increased font size
result_text.grid(column=0, row=5, columnspan=2, padx=10,
                 pady=(40, 80))  

window.mainloop()