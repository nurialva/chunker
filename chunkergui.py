#!/usr/bin/env python3
"""
JSONL File Splitter with GUI
Split JSONL file into chunks with customizable chunk size
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from threading import Thread
import json
import datetime

class JSONLSplitterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JSONL File Splitter")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.chunk_size = tk.StringVar(value="50")
        self.output_dir = tk.StringVar()
        self.is_running = False
        self.is_stopped = False
        
        # Available chunk sizes
        self.chunk_sizes = ["10", "20", "50", "100", "200", "500", "1000", "2000", "5000"]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========================================
        # HEADER
        # ========================================
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(
            header_frame, 
            text="📄 JSONL File Splitter",
            font=('Arial', 18, 'bold')
        )
        title.pack()
        
        subtitle = ttk.Label(
            header_frame,
            text="Split large JSONL files into smaller chunks",
            font=('Arial', 10)
        )
        subtitle.pack()
        
        # ========================================
        # FILE SELECTION
        # ========================================
        file_frame = ttk.LabelFrame(main_frame, text="📁 Input File", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_row = ttk.Frame(file_frame)
        file_row.pack(fill=tk.X)
        
        self.file_entry = ttk.Entry(
            file_row, 
            textvariable=self.input_file,
            state='readonly',
            font=('Consolas', 10)
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_browse = ttk.Button(
            file_row, 
            text="📂 Browse",
            command=self.browse_file,
            width=12
        )
        btn_browse.pack(side=tk.RIGHT)
        
        # File info
        self.file_info = ttk.Label(
            file_frame,
            text="No file selected",
            font=('Arial', 9),
            foreground='gray'
        )
        self.file_info.pack(anchor=tk.W, pady=(5, 0))
        
        # ========================================
        # CHUNK SIZE SELECTION
        # ========================================
        chunk_frame = ttk.LabelFrame(main_frame, text="⚙️ Chunk Size", padding="10")
        chunk_frame.pack(fill=tk.X, pady=(0, 15))
        
        chunk_row = ttk.Frame(chunk_frame)
        chunk_row.pack(fill=tk.X)
        
        ttk.Label(chunk_row, text="Lines per chunk:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.chunk_combo = ttk.Combobox(
            chunk_row,
            textvariable=self.chunk_size,
            values=self.chunk_sizes,
            state='readonly',
            width=10
        )
        self.chunk_combo.pack(side=tk.LEFT)
        
        # Custom chunk size
        ttk.Label(chunk_row, text="Or custom:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.custom_entry = ttk.Entry(
            chunk_row,
            width=10
        )
        self.custom_entry.pack(side=tk.LEFT)
        self.custom_entry.bind('<KeyRelease>', self.on_custom_chunk)
        
        ttk.Label(
            chunk_frame,
            text="💡 Select chunk size or enter custom value (e.g., 75)",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # ========================================
        # OUTPUT DIRECTORY
        # ========================================
        output_frame = ttk.LabelFrame(main_frame, text="📂 Output Directory", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_row = ttk.Frame(output_frame)
        output_row.pack(fill=tk.X)
        
        self.output_entry = ttk.Entry(
            output_row,
            textvariable=self.output_dir,
            state='readonly',
            font=('Consolas', 10)
        )
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_output = ttk.Button(
            output_row,
            text="📁 Browse",
            command=self.browse_output,
            width=12
        )
        btn_output.pack(side=tk.RIGHT)
        
        self.output_info = ttk.Label(
            output_frame,
            text="Will be created in same directory as input file",
            font=('Arial', 8),
            foreground='gray'
        )
        self.output_info.pack(anchor=tk.W, pady=(5, 0))
        
        # ========================================
        # ACTION BUTTONS
        # ========================================
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_split = ttk.Button(
            action_frame,
            text="🚀 Split File",
            command=self.start_split,
            width=20
        )
        self.btn_split.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = ttk.Button(
            action_frame,
            text="⏹ Stop",
            command=self.stop_split,
            state='disabled',
            width=20
        )
        self.btn_stop.pack(side=tk.LEFT)
        
        # ========================================
        # PROGRESS BAR
        # ========================================
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(
            progress_frame,
            text="Ready to split",
            font=('Arial', 9)
        )
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ========================================
        # LOG OUTPUT
        # ========================================
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=('Consolas', 9),
            background='#1e1e1e',
            foreground='#d4d4d4',
            insertbackground='white'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log colors
        self.log_text.tag_configure('success', foreground='#4ade80')
        self.log_text.tag_configure('error', foreground='#ef4444')
        self.log_text.tag_configure('info', foreground='#60a5fa')
        self.log_text.tag_configure('warning', foreground='#f59e0b')
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ========================================
        # INITIAL LOG
        # ========================================
        self.log("🚀 JSONL File Splitter GUI started", 'info')
        self.log("💡 Select a JSONL file to begin", 'info')
        
    # ========================================
    # EVENT HANDLERS
    # ========================================
    
    def browse_file(self):
        """Browse for input file"""
        file_path = filedialog.askopenfilename(
            title="Select JSONL File",
            filetypes=[
                ("JSONL files", "*.jsonl"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.input_file.set(file_path)
            self.update_file_info(file_path)
            self.update_output_dir(file_path)
            self.log(f"📂 Selected: {os.path.basename(file_path)}", 'info')
    
    def browse_output(self):
        """Browse for output directory"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory"
        )
        
        if dir_path:
            self.output_dir.set(dir_path)
            self.log(f"📁 Output directory: {dir_path}", 'info')
    
    def update_file_info(self, file_path):
        """Update file information display"""
        try:
            path = Path(file_path)
            size = path.stat().st_size
            size_str = self.format_size(size)
            
            # Count lines
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            self.file_info.config(
                text=f"📄 {path.name} | Size: {size_str} | Lines: {line_count:,}"
            )
            self.status_bar.config(text=f"Loaded: {path.name}")
            
        except Exception as e:
            self.file_info.config(text=f"Error reading file: {e}")
            self.log(f"❌ Error reading file: {e}", 'error')
    
    def update_output_dir(self, file_path):
        """Auto-set output directory"""
        input_path = Path(file_path)
        default_output = input_path.parent / f"{input_path.stem}_split"
        self.output_dir.set(str(default_output))
        self.output_info.config(
            text=f"📁 Will save to: {default_output}"
        )
    
    def on_custom_chunk(self, event):
        """Handle custom chunk size input"""
        value = self.custom_entry.get()
        if value.isdigit() and int(value) > 0:
            self.chunk_size.set(value)
            self.chunk_combo.set('custom')
    
    # ========================================
    # SPLIT FUNCTION
    # ========================================
    
    def start_split(self):
        """Start the splitting process"""
        if self.is_running:
            return
        
        input_file = self.input_file.get()
        if not input_file:
            messagebox.showerror("Error", "Please select a JSONL file first!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Selected file does not exist!")
            return
        
        # Get chunk size
        chunk_size_str = self.chunk_size.get()
        if chunk_size_str == 'custom':
            chunk_size_str = self.custom_entry.get()
        
        if not chunk_size_str.isdigit() or int(chunk_size_str) <= 0:
            messagebox.showerror("Error", "Invalid chunk size! Please enter a positive number.")
            return
        
        chunk_size = int(chunk_size_str)
        
        # Get output directory
        output_dir = self.output_dir.get()
        if not output_dir:
            # Use default
            input_path = Path(input_file)
            output_dir = str(input_path.parent / f"{input_path.stem}_split")
            self.output_dir.set(output_dir)
        
        # Confirm if directory exists
        if os.path.exists(output_dir) and os.listdir(output_dir):
            if not messagebox.askyesno(
                "Directory Exists",
                f"Output directory already contains files:\n{output_dir}\n\nOverwrite?"
            ):
                return
        
        # Reset stop flag
        self.is_stopped = False
        
        # Start splitting in thread
        self.is_running = True
        self.btn_split.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        self.log(f"🚀 Starting split: {os.path.basename(input_file)}", 'info')
        self.log(f"📊 Chunk size: {chunk_size:,} lines", 'info')
        self.log(f"📁 Output: {output_dir}", 'info')
        
        Thread(
            target=self.split_jsonl,
            args=(input_file, chunk_size, output_dir),
            daemon=True
        ).start()
    
    def split_jsonl(self, input_file, chunk_size, output_dir):
        """Split JSONL file (runs in thread)"""
        try:
            input_path = Path(input_file)
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Count total lines first
            self.update_status("Counting lines...")
            total_lines = 0
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        total_lines += 1
            
            if total_lines == 0:
                self.log("❌ File is empty or contains no valid lines", 'error')
                self.finish_split()
                return
            
            self.log(f"📊 Total lines: {total_lines:,}", 'info')
            
            # Split the file
            file_count = 0
            current_lines = []
            processed_lines = 0
            
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if self.is_stopped:
                        self.log("⏹ Split stopped by user", 'warning')
                        self.finish_split()
                        return
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    current_lines.append(line)
                    processed_lines += 1
                    
                    if len(current_lines) >= chunk_size:
                        file_count += 1
                        output_file = output_path / f"part_{file_count:04d}.jsonl"
                        with open(output_file, 'w', encoding='utf-8') as out:
                            out.write('\n'.join(current_lines))
                        
                        # Update progress
                        progress = (processed_lines / total_lines) * 100
                        self.root.after(0, lambda p=progress, pl=processed_lines, tl=total_lines: 
                                      self.update_progress(p, pl, tl))
                        
                        if file_count % 10 == 0:  # Log every 10 files
                            self.log(f"  📄 Part {file_count:04d}: {len(current_lines):,} lines", 'success')
                        
                        current_lines = []
                
                # Write remaining lines
                if current_lines:
                    file_count += 1
                    output_file = output_path / f"part_{file_count:04d}.jsonl"
                    with open(output_file, 'w', encoding='utf-8') as out:
                        out.write('\n'.join(current_lines))
                    self.log(f"  ✅ Part {file_count:04d}: {len(current_lines):,} lines (final)", 'success')
            
            self.log(f"\n✅ Success! Split {total_lines:,} lines into {file_count:,} files", 'success')
            self.log(f"📁 Files saved in: {output_path}", 'info')
            
            self.root.after(0, lambda: self.update_progress(100, total_lines, total_lines))
            self.root.after(0, lambda: messagebox.showinfo(
                "Split Complete",
                f"✅ Successfully split {total_lines:,} lines into {file_count:,} files!\n\n📁 Files saved in:\n{output_path}"
            ))
            
        except Exception as e:
            self.log(f"❌ Error: {e}", 'error')
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to split file:\n{e}"))
        
        finally:
            self.finish_split()
    
    def stop_split(self):
        """Stop the splitting process"""
        self.is_stopped = True
        self.log("⏹ Stopping split...", 'warning')
        self.btn_stop.config(state='disabled')
    
    def finish_split(self):
        """Clean up after split completes or stops"""
        self.is_running = False
        self.is_stopped = False
        self.root.after(0, lambda: self.btn_split.config(state='normal'))
        self.root.after(0, lambda: self.btn_stop.config(state='disabled'))
        self.update_status("Ready")
    
    # ========================================
    # UI UPDATE FUNCTIONS
    # ========================================
    
    def update_progress(self, progress, processed, total):
        """Update progress bar"""
        self.progress_var.set(min(progress, 100))
        self.progress_label.config(
            text=f"Processing: {processed:,} / {total:,} lines ({progress:.1f}%)"
        )
    
    def update_status(self, text):
        """Update status bar"""
        self.root.after(0, lambda: self.status_bar.config(text=text))
    
    def log(self, message, tag='info'):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        formatted = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self.log_text.insert(tk.END, formatted, tag))
        self.root.after(0, lambda: self.log_text.see(tk.END))
    
    def format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

# ========================================
# MAIN
# ========================================

def main():
    root = tk.Tk()
    app = JSONLSplitterGUI(root)
    
    # Set icon if available
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
