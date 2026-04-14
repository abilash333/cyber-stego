import streamlit as st
from PIL import Image
import io

# --- ENCRYPTION LOGIC ---
def apply_password(message, password):
    # This mixes the message with the password so it's scrambled
    return "".join(chr(ord(c) ^ ord(password[i % len(password)])) for i, c in enumerate(message))

def text_to_bin(message):
    return bin(int.from_bytes(message.encode(), 'big')).replace('0b', '') + '1111111111111110'

def bin_to_text(binary_str):
    try:
        binary_str = binary_str.split('1111111111111110')[0]
        n = int(binary_str, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    except:
        return None

# --- UI SETUP ---
st.set_page_config(page_title="Secure-Stego", page_icon="🔐")
st.title("🔐 Secure Ghost Encoder")

tab1, tab2 = st.tabs(["📥 Secure Encode", "📤 Secure Decode"])

with tab1:
    st.subheader("1. Hide & Encrypt")
    uploaded_file = st.file_uploader("Upload PNG", type=["png"], key="enc")
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        msg = st.text_input("Message:")
        pwd = st.text_input("Set Password:", type="password") # Hides the typing
        
        if st.button("Lock Message in Image") and msg and pwd:
            # First, scramble the message with the password
            secure_msg = apply_password(msg, pwd)
            binary_msg = text_to_bin(secure_msg)
            
            # Hide the bits
            pixels = list(img.getdata())
            new_pixels = []
            msg_idx = 0
            for p in pixels:
                if msg_idx < len(binary_msg):
                    new_red = (p[0] & ~1) | int(binary_msg[msg_idx])
                    new_pixels.append((new_red, p[1], p[2]))
                    msg_idx += 1
                else:
                    new_pixels.append(p)
            
            new_img = Image.new("RGB", img.size)
            new_img.putdata(new_pixels)
            buf = io.BytesIO()
            new_img.save(buf, format="PNG")
            st.success("Encrypted and Hidden!")
            st.download_button("Download Secure PNG", buf.getvalue(), "secure.png")

with tab2:
    st.subheader("2. Decrypt & Reveal")
    decode_file = st.file_uploader("Upload Secure PNG", type=["png"], key="dec")
    
    if decode_file:
        pwd_attempt = st.text_input("Enter Password to Unlock:", type="password")
        
        if st.button("Unlock Message") and pwd_attempt:
            pixels = list(Image.open(decode_file).getdata())
            binary_msg = "".join([str(p[0] & 1) for p in pixels])
            
            raw_data = bin_to_text(binary_msg)
            
            if raw_data:
                # Scramble it back using the password attempt
                final_msg = apply_password(raw_data, pwd_attempt)
                st.info(f"🔓 Decrypted Message: {final_msg}")
            else:
                st.error("No hidden data found.")
