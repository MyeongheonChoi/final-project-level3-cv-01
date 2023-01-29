import streamlit as st

st.set_page_config(page_icon="🔎", layout="wide")
st.header("안녕하세요😁 당신만의 면접 도우미, **HEY-I**_v1.0 입니다!")


with st.form("my_form"):
    name = st.text_input("이름을 입력하세요")
    num = st.number_input("원하는 네 자리 수를 입력하세요",min_value=0,max_value=9999)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"{name}_{num} 확인됐습니다!")
    else:
        st.warning('입력해주세요!', icon="⚠️")
st.write('다음 단계로 넘어가세요!')        
st.session_state.name = name
st.session_state.num = num


    
print(st.session_state.name, st.session_state.num)
