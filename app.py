import streamlit as st
from PIL import Image
import io

# --- CORE LOGIC (The "Brain") ---

def apply_password(message, password):
    # This line automatically removes any spaces from the password
    # to prevent the "ldb}" gibberish error we discussed.
    clean_password = password.replace(" ", "")
    if not clean_password:
        return message # Fallback if user only enters spaces
    return "".join(chr(ord(c) ^ ord(clean_password[i % len(clean_password)])) for i, c in enumerate(message))

def text_to_bin(message):
    # Converts your scrambled message into binary (0s and 1s)
    return bin(int.from_bytes(message.encode(), 'big')).replace('0b', '') + '1111111111111110'

def bin_to_text(binary_str):
    # Extracts the binary bits and turns them back into text
    try:
        binary_str = binary_str.split('1111111111111110')[0]
        n = int(binary_str, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    except:
        return None

# --- UI CONFIGURATION (The "Look") ---

st.set_page_config(page_title="CipherImage Pro", page_icon="🛡️", layout="wide")

# Custom CSS for a professional SaaS feel
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 5px; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Branding
st.sidebar.title("🛡️ CipherImage Pro")
st.sidebar.markdown("---")
st.sidebar.info("v2.1.0 - Secure Steganography")
st.sidebar.write("Tip: If you use a password with spaces, I will automatically clean it for you!")

# Main Title Section
st.title("🛡️ Secure Your Data in Pixels")
st.write("Professional-grade tool for hiding encrypted messages inside images.")
st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🔒 Encode Engine", "🔓 Decode Engine", "📋 Technology"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Upload Media")
        file = st.file_uploader("Upload an image (JPG, JPEG, or PNG)", type=["png", "jpg", "jpeg"])
        if file:
            # Automatic JPG to PNG converter
            img = Image.open(file).convert("RGB")
            st.image(img, caption="Ready for Encoding", use_container_width=True)
            if file.type != "image/png":
                st.warning("🔄 Auto-converting your JPG to PNG for safety.")

    with col2:
        st.subheader("2. Secure Config")
        secret_text = st.text_area("Secret Message", placeholder="Enter your confidential data...")
        passkey = st.text_input("Encryption Key", type="password", placeholder="Set a password")
        
        if st.button("🚀 Process & Generate Vault"):
            if file and secret_text and passkey:
                with st.spinner("Locking data into pixels..."):
                    # Scramble with password (space-cleaned)
                    scrambled = apply_password(secret_text, passkey)
                    bits = text_to_bin(scrambled)
                    
                    # Embedding logic
                    pixels = list(img.getdata())
                    new_pixels = []
                    idx = 0
                    for p in pixels:
                        if idx < len(bits):
                            # Change the Red channel bit
                            new_r = (p[0] & ~1) | int(bits[idx])
                            new_pixels.append((new_r, p[1], p[2]))
                            idx += 1
                        else:
                            new_pixels.append(p)
                    
                    # Save the result
                    out_img = Image.new("RGB", img.size)
                    out_img.putdata(new_pixels)
                    buf = io.BytesIO()
                    out_img.save(buf, format="PNG")
                    
                    st.success("Encoding Complete!")
                    st.download_button("💾 Download Encrypted Asset", buf.getvalue(), "vault.png")
            else:
                st.error("Please provide an image, a message, and a password.")

with tab2:
    st.subheader("Decrypt Asset")
    d_file = st.file_uploader("Upload the 'Vault' PNG", type=["png"], key="dec_uploader")
    
    if d_file:
        d_col1, d_col2 = st.columns([1, 2])
        with d_col1:
            st.image(d_file, use_container_width=True)
        with d_col2:
            d_pass = st.text_input("Access Key", type="password", key="decode_pass")
            if st.button("🔍 Extract & Decrypt"):
                with st.spinner("Scanning bit-layers..."):
                    pixels = list(Image.open(d_file).getdata())
                    bits = "".join([str(p[0] & 1) for p in pixels])
                    raw = bin_to_text(bits)
                    
                    if raw:
                        # Decrypt with password (space-cleaned)
                        result = apply_password(raw, d_pass)
                        st.success("Access Granted")
                        st.info("The Hidden Message:")
                        st.code(result, language=None)
                        st.warning("☝️ If the text looks like 'ldb}' or gibberish, your Password was wrong!")
                    else:
                        st.error("Access Denied: No steganographic data detected.")

with tab3:
    st.header("Technical Overview")
    st.write("""
    **CipherImage Pro** uses a dual-protection layer:
    1. **XOR Stream Cipher**: The message is XORed with your key. If the key is 'hai guys', it is processed as 'haiguys'.
    2. **LSB Encoding**: We modify the *Least Significant Bit* of the red channel. This is invisible to the human eye.
    """)
    st.table({
        "Feature": ["Lossless Rendering", "Key Scrubbing", "Bit-Layer"],
        "Details": ["PNG Output (Forced)", "Auto Space-Removal", "Red Channel LSB"]
    })
