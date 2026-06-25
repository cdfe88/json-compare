import streamlit as st
import json
import pandas as pd
from pathlib import Path
from deepdiff import DeepDiff
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

def flatten_path(path_obj):
    return (
        path_obj.replace("root", "")
        .replace("['", "")
        .replace("']", "")
        .replace("']['", ".")
        .replace("'][", ".")
        .strip(".")
    )

def index_json_files(uploaded_files):
    if not uploaded_files:
        return {}
    # Only index .json files based on their relative path name
    return {f.name: f for f in uploaded_files}

def compare_folders(before_folder, after_folder):
    before_files = index_json_files(before_folder)
    after_files = index_json_files(after_folder)
    common_files = sorted(list(set(before_files.keys()).intersection(set(after_files.keys()))))
    count=len(common_files)
    c=0
    records = []
    for fname in common_files:
        old_data=json.load(before_files[fname])
        new_data=json.load(after_files[fname])
        diff=DeepDiff(old_data, new_data, ignore_order=True, view='tree')

        if diff:
            for change_type, changes in diff.items():
                for change in changes:
                    records.append([
                        fname,
                        change_type,
                        flatten_path(change.path()),
                        getattr(change, 't1', None),
                        getattr(change, 't2', None)
                    ])
        else:
            records.append([fname, 'no_change', None, None, None])
        c+=c/count
        mybar.progress(c, text='Running...')
    df = pd.DataFrame(records, columns=['file','change_type','parameter','old','new'])
    return df


st.sidebar.header("Upload Folders")
dir_before = st.sidebar.file_uploader("Before", accept_multiple_files="directory", key="dir_a", type='.json')
dir_after = st.sidebar.file_uploader("After", accept_multiple_files="directory", key="dir_b",type='.json')

if st.button('Compare Folders',disabled=not(dir_before and dir_after)):
    diff=compare_folders(dir_before,dir_after)
else: diff=pd.DataFrame()

mybar=st.progress(0.0,'Running...')

st.dataframe(diff)