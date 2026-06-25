import streamlit as st
import json
import pandas as pd
from deepdiff import DeepDiff

diff=pd.DataFrame()
st.header("Upload Folders")
c1,c2=st.columns(2)
with c1:
    dir_before = st.file_uploader("Before", accept_multiple_files="directory", key="dir_a", type='.json')
with c2:
    dir_after = st.file_uploader("After", accept_multiple_files="directory", key="dir_b",type='.json')
mybar=st.progress(0.0,'Waiting...')

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
    return {f.name.rsplit("/", 1)[1]: f for f in uploaded_files}

def compare_folders(before_folder, after_folder):
    before_files = index_json_files(before_folder)
    after_files = index_json_files(after_folder)
    common_files = sorted(list(set(before_files.keys()).intersection(set(after_files.keys()))))
    count=len(common_files)
    c=0.0
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
        c+=1.0
        mybar.progress(c/count, text=f"Progress: {c/count*100}%")
    df = pd.DataFrame(records, columns=['file','change_type','parameter','old','new'])
    return df


if dir_before and dir_after:
    diff=compare_folders(dir_before,dir_after)


st.dataframe(diff)