import tkinter as tk
from tkinter import ttk
import json 
from Process import *



class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Page GUI")

        self.notebook = ttk.Notebook(root)

        # Users Database
        self.users = json.load(open("users.json", "r"))

        # Create pages
        self.enrollment_page = ttk.Frame(self.notebook)
        self.identification_page = ttk.Frame(self.notebook)
        self.verification_page = ttk.Frame(self.notebook)

        self.notebook.add(self.enrollment_page, text="Enrollment")
        self.notebook.add(self.identification_page, text="Identification")
        self.notebook.add(self.verification_page, text="Verification")

        self.notebook.pack(expand=True, fill="both")

        # Enrollment Page
        self.enrollment_label = tk.Label(self.enrollment_page, text="Enter your name and ID:")
        self.enrollment_label.pack(pady=10)

        self.name_var = tk.StringVar()
        self.id_var = tk.StringVar()

        tk.Entry(self.enrollment_page, textvariable=self.name_var, width=30).pack(pady=5)
        tk.Entry(self.enrollment_page, textvariable=self.id_var, width=30).pack(pady=5)

        self.enroll_button = tk.Button(self.enrollment_page, text="Enroll", command=self.enroll_user)
        self.enroll_button.pack(pady=10)

        # Identification Page
        self.scan_button = tk.Button(self.identification_page, text="Scan", command=self.scan_fingerprint)
        self.scan_button.pack(pady=10)
        self.identification_result_ID = None

        # Verification Page
        self.verification_label = tk.Label(self.verification_page, text="Enter your ID:")
        self.verification_label.pack(pady=10)

        self.id_verification_var = tk.StringVar()
        tk.Entry(self.verification_page, textvariable=self.id_verification_var, width=30).pack(pady=5)

        self.verify_button = tk.Button(self.verification_page, text="Scan", command=self.verify_user)
        self.verify_button.pack(pady=10)
    
    def foo(self):
        import time
        time.sleep(3)
        return True
    
    def enroll_user(self):
        self.enroll_button.config(state=tk.DISABLED)

        name = self.name_var.get()
        user_id = self.id_var.get()
        
        # Check if user ID is valid
        user_id_list = self.users.keys()
        if user_id in user_id_list:
            bad_user_id_label = tk.Label(self.enrollment_page, text="user ID already exists")
            bad_user_id_label.pack(pady=10)
            self.root.after(2000, bad_user_id_label.destroy)
            self.reset_enrollment_page()
            return

        # Add user to database
        with open("users.json", "w") as f:
            self.users[user_id] = name
            json.dump(self.users, f)
        self.users = json.load(open("users.json", "r"))
            
        self.enrollment_label.config(text="Please place your fingerprint on the scanner, it will scan within 5 seconds")

        result=enrollement(user_id)
        
        if result:
            self.enrollment_label.config(text="Enrollment successful!")
        else:
            self.enrollment_label.config(text="Enrollment failed, please try again")

        # Return to the enrollment prompt after a delay
        self.root.after(2000, self.reset_enrollment_page)

    def reset_enrollment_page(self):
        self.enroll_button.config(state=tk.NORMAL)
        # Clear entry fields and confirmation label
        self.name_var.set("")
        self.id_var.set("")
        self.enrollment_label.config(text="Enter your name and ID:")

        # Delete confirmation label if it exists
        for widget in self.enrollment_page.winfo_children():
            if isinstance(widget, tk.Label) and "Enrollment successful!" in widget.cget("text"):
                widget.destroy()

    def scan_fingerprint(self):
        """identification"""
        # Disable the "Scan" button during the scanning process
        self.scan_button.config(state=tk.DISABLED)

        # returns user's id
        identified_id = Identification()

        self.display_identification_result(identified_id)

    def display_identification_result(self, identified_id):
        """reset id screen"""
        # Enable the "Scan" button after the scanning process
        self.scan_button.config(state=tk.NORMAL)

        id_result = tk.Label(self.identification_page, text="")
        if identified_id is not None:
            # TODO: print name as well as ID
            id_result.config(text=f"Finger identified as {self.users[identified_id]}, ID:{identified_id}")
            id_result.pack(pady=10)
        else:
            id_result.config(text="Could not be identified")
            id_result.pack(pady=10)
        
        self.root.after(2000, id_result.destroy)

    def verify_user(self):
        self.verify_button.config(state=tk.DISABLED)
        user_id_verification = self.id_verification_var.get()

        result = Verification(user_id_verification)

        if result is None:
            verification_result_label = tk.Label(self.verification_page, text=f"User id not in database")
        elif result:
            # Display the verified name
            verification_result_label = tk.Label(self.verification_page, text=f"yes, this is {self.users[user_id_verification]}, ID:{user_id_verification}")
        else:
            verification_result_label = tk.Label(self.verification_page, text=f"No, this is not {user_id_verification}")
        verification_result_label.pack(pady=10)


        # Clear the result label after a delay
        self.verify_button.config(state=tk.ACTIVE)
        self.root.after(2000, verification_result_label.pack_forget)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
