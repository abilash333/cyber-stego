import streamlit as st
from PIL import Image
import io

# --- CORE LOGIC ---
def text_to_bin(message):
    # Converts text to binary bits
    return bin(int.from_bytes(message.encode(), 'big')).replace('0b', '') + '1111111111111110'

def bin_to_text(binary_str):
    # Converts binary bits back to text
    try:
        binary_str = binary_str.split('1111111111111110')[0]
        n = int(binary_str, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    except:
        return "❌ Error: No hidden message found."

# --- UI SETUP ---
st.set_page_config(page_title="Cyber-Stego", page_icon="🔐")

# Sidebar
st.sidebar.title("🚀 Quick Guide")
st.sidebar.info("This tool hides text inside the pixels of an image.")
st.sidebar.warning("❗ Use ONLY .PNG files. JPEGs will scramble the secret.")

# Main Title (Simplified to avoid TypeError)
st.title("🔐 Cyber-Stego Encoder")
st.write("The art of hiding messages in plain sight.")

tab1, tab2 = st.tabs(["📥 Encode (Hide)", "📤 Decode (Reveal)"])

with tab1:
    st.subheader("Hide a Secret")
    # This is the "Creative" text you asked for:
    st.error("📸 IMPORTANT: This only works with PNG images.")
    
    uploaded_file = st.file_uploader("Upload your base image", type=["png"], key="enc_upload")
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Ready to encode", use_container_width=True)
        
        secret_msg = st.text_input("🤫 Secret Message:", placeholder="Type your secret here...")
        
        if st.button("✨ Generate Ghost Image") and secret_msg:
            with st.spinner('Mixing bits...'):
                binary_msg = text_to_bin(secret_msg)
                pixels = list(img.getdata())
                new_pixels = []
                msg_idx = 0
                
                for pixel in pixels:
                    if msg_idx < len(binary_msg):
                        # Modify the Red channel bit
                        new_red = (pixel[0] & ~1) | int(binary_msg[msg_idx])
                        new_pixels.append((new_red, pixel[1], pixel[2]))
                        msg_idx += 1
                    else:
                        new_pixels.append(pixel)
                
                new_img = Image.new(img.mode, img.size)
                new_img.putdata(new_pixels)
                
                # Save to memory
                buf = io.BytesIO()
                new_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.balloons()
                st.success("Hidden! Now download and send it.")
                st.download_button(
                    label="💾 Download Result", 
                    data=byte_im, 
                    file_name="ghost_image.png", 
                    mime="image/png"
                )

with tab2:
    st.subheader("Reveal a Secret")
    decode_file = st.file_uploader("Upload a Ghost PNG", type=["png"], key="dec_upload")
    
    if decode_file:
        img = Image.open(decode_file).convert("RGB")
        st.image(img, width=250)
        
        if st.button("🔍 Extract Secret"):
            pixels = list(img.getdata())
            binary_msg = ""
            for pixel in pixels:
                binary_msg += str(pixel[0] & 1)
                if '1111111111111110' in binary_msg:
                    break
            
            result = bin_to_text(binary_msg)
            st.info("Hidden Message Found:")
            st.code(result)