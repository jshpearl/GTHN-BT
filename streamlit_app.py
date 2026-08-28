import streamlit as st
import requests
import datetime
import json
import os

# ==========================================================
# 1. CẤU HÌNH TRANG & CSS CUSTOMIZATION (TONG PASTEL)
# ==========================================================
st.set_page_config(
    page_title="Bài tập Giáo trình Hán ngữ (1)",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for Pastel Styling
st.markdown("""
<style>
    /* Nền trang màu kem nhạt */
    .stApp {
        background-color: #FAF6F0;
    }
    
        /* Font và màu chữ tối tương phản cực kỳ rõ nét và đậm màu */
    body, p, label, .quiz-card, h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Tối ưu hóa chữ hiển thị trong hộp chọn Selectbox của Streamlit */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        font-size: 18px !important;
    }
    
    /* Chữ được chọn hiển thị trong hộp - ĐẬM ĐEN rõ nét */
    div[data-testid="stSelectbox"] div[role="button"] {
        font-size: 18px !important;
        color: #111111 !important;
        font-weight: bold !important;
    }
    
    /* Nền trắng và viền pastel xinh xắn cho bảng danh sách xổ xuống */
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 2px solid #FFD1DC !important;
        border-radius: 12px !important;
    }
    
    /* KHÓA CỨNG nền trắng và chữ đen đậm rõ nét cho tất cả các lựa chọn dropdown */
    div[data-baseweb="popover"] li, ul[role="listbox"] li, [role="option"] {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 12px 16px !important;
    }
    
    /* Đảm bảo toàn bộ chữ bên trong li và option (kể cả nested spans/divs) đều có màu đen đậm */
    div[data-baseweb="popover"] li *, [role="option"] * {
        color: #111111 !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* Hiệu ứng di chuột vào lựa chọn (Hover) đổi sang màu hồng pastel nhạt */
    div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover, [role="option"]:hover,
    div[data-baseweb="popover"] li:hover *, [role="option"]:hover * {
        background-color: #FFF1F3 !important;
        color: #111111 !important;
    }
    /* Che/An logo va cac nut o goc phai tren */
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# URL Webhook Google Sheets
WEBHOOK_URL = st.secrets.get("GOOGLE_SHEET_WEBHOOK", "https://script.google.com/macros/s/AKfycbyWd_lmpFBAQP1ZPa-X_Njwvqj-Frii7PThZV7yL8OmaFDJYVNjCeUTaP5eiapalRDX/exec")

# ==========================================================
# 2. NGÂN HÀNG CÂU HỎI CHUẨN 3 BÀI 6, 7, 8 (MỖI BÀI 30 CÂU)
# ==========================================================
# Các câu hỏi tuyệt đối không chứa tiếng Việt dịch nghĩa trong text, chỉ hiển thị chữ Hán và Pinyin, in đậm
QUESTIONS = {
    'bai_8': {
        'title': 'BÀI 8: BẠN ĂN CÁI GÌ? / 你吃什么',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai
            {'id': 1, 'type': 'tf', 'text': '1. 吃饭 / Chī fàn', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '吃饭 (Chī fàn)', 'explanation': 'Audio phát chính xác cụm từ "吃饭" (Ăn cơm).'},
            {'id': 2, 'type': 'tf', 'text': '2. 请坐 / Qǐng zuò', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '请坐 (Qǐng zuò)', 'explanation': 'Audio phát chính xác cụm từ "请坐" (Xin mời ngồi).'},
            {'id': 3, 'type': 'tf', 'text': '3. 美国人 / Měiguó rén', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '美国人 (Měiguó rén)', 'explanation': 'Hình ảnh không khớp với từ chỉ người nước Mỹ.'},
            {'id': 4, 'type': 'tf', 'text': '4. 朋友 / Péngyou', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '朋友 (Péngyou)', 'explanation': 'Nội dung hình ảnh và cụm từ "朋友" không đồng nhất.'},
            {'id': 5, 'type': 'tf', 'text': '5. 请喝茶 / Qǐng hē chá', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '请喝茶 (Qǐng hē chá)', 'explanation': 'Audio phát chính xác cụm từ "请喝茶" (Mời uống trà).'},            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '6. ', 'audio_part': 2, 'correct': 'D', 'script': '男：他叫什么名字？\n女：他叫大卫。他是美国人。', 'explanation': 'Hội thoại nhắc đến David - người Mỹ (Hình D).'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '7. ', 'audio_part': 2, 'correct': 'B', 'script': '男：你想吃米饭吗？\n女：我想 eat。', 'explanation': 'Hội thoại nhắc đến muốn ăn cơm (米饭), khớp với hình B.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '8. ', 'audio_part': 2, 'correct': 'F', 'script': '男：中午你去哪儿吃饭？\n女：我去学生食堂。', 'explanation': 'Nhân vật nữ trả lời đi ăn cơm ở nhà ăn sinh viên (学生食堂), khớp hình F.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '9. ', 'audio_part': 2, 'correct': 'A', 'script': '男：我请你喝 coffee 怎么样？\n女：太好了，谢谢！', 'explanation': 'Mời uống cà phê (喝咖啡), khớp hình A.'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '10. ', 'audio_part': 2, 'correct': 'E', 'script': '男：老师，您叫什么名字？\n女：我叫李月。', 'explanation': 'Học sinh hỏi tên giáo viên và cô trả lời Lý Nguyệt (李月), khớp hình E.'},            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A. 包子 / bāozi', 'B. 面条儿 / miàntiáor', 'C. 米饭 / mǐfàn'], 'text': '11. 他不想吃什么？', 'audio_part': 3, 'correct': 'C', 'script': '我这几天中午吃的都是米饭，不想吃了。\n问：他不想吃什么？', 'explanation': 'Nhân vật nam nói đã chán ăn cơm (米饭). Chọn C.'},
            {'id': 12, 'type': 'mc', 'options': ['A. 美国人 / Měiguó rén', 'B. 中国人 / Zhōngguó rén', 'C. 日本人 / Rìběn rén'], 'text': '12. 他是哪国人？', 'audio_part': 3, 'correct': 'B', 'script': '他叫王心，他是中国人。\n问：他是哪国人？', 'explanation': 'Vương Tâm là người Trung Quốc (中国人). Chọn B.'},
            {'id': 13, 'type': 'mc', 'options': ['A. 王方 / Wáng Fāng', 'B. 李心 / Lǐ Xīn', 'C. 玛丽 / Mǎlì'], 'text': '13. 她叫什么名字？', 'audio_part': 3, 'correct': 'B', 'script': '她叫李心，是我的中国朋友。\n问：她叫什么名字？', 'explanation': 'Tên cô ấy là Lý Tâm (李心). Chọn B.'},
            {'id': 14, 'type': 'mc', 'options': ['A. 他的爸爸 / tā de bàba', 'B. 他的朋友 / tā de péngyou', 'C. 他的老师 / tā de lǎoshī'], 'text': '14. 前面那个人是谁？', 'audio_part': 3, 'correct': 'C', 'script': '前面那个人是我的老师，不是我爸爸。\n问：前面那个人是谁？', 'explanation': 'Người phía trước là giáo viên của tôi (我的老师). Chọn C.'},
            {'id': 15, 'type': 'mc', 'options': ['A. 公园 / gōngyuán', 'B. 银行 / yínháng', 'C. 学校 / xuéxiào'], 'text': '15. 他们骑车去哪儿？', 'audio_part': 3, 'correct': 'A', 'script': '我和丽丽骑车去公园。\n问：他们骑车去哪儿？', 'explanation': 'Họ đạp xe đi công viên (公园). Chọn A.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình
            {'id': 16, 'type': 'tf', 'text': '16. bāozi / 包子', 'correct': 'Đúng (✓)', 'explanation': 'Khớp với hình ảnh bánh bao.'},
            {'id': 17, 'type': 'tf', 'text': '17. jīdàn / 鸡蛋', 'correct': 'Sai (✗)', 'explanation': 'Hình ảnh trứng gà mái không khớp với từ vựng trong sách bài tập.'},
            {'id': 18, 'type': 'tf', 'text': '18. chī jiǎozi / 吃饺子', 'correct': 'Sai (✗)', 'explanation': 'Hình ảnh ăn sủi cảo không khớp với từ vựng trong sách bài tập.'},
            {'id': 19, 'type': 'tf', 'text': '19. xiě Hànzì / 写汉字', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh tay cầm bút lông viết chữ Hán.'},
            {'id': 20, 'type': 'tf', 'text': '20. hē píjiǔ / 喝啤酒', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh hai cốc bia tươi.'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A. 去食堂。 / Qù shítáng.', 'B. 这些是馒头。 / Zhèxiē shì mántou.', 'C. 不喝，我喝茶。 / Bù hē, wǒ hē chá.', 'D. 三个。 / Sān ge.', 'E. 我吃面条儿。 / Wǒ chī miàntiáor.'], 'text': '21. 你去哪儿吃饭？ / Nǐ qù nǎr chī fàn?', 'correct': 'A', 'explanation': 'Hỏi ăn ở đâu -> Trả lời đi nhà ăn (去食堂).'},
            {'id': 22, 'type': 'mc', 'options': ['A. 去食堂。 / Qù shítáng.', 'B. 这些是馒头。 / Zhèxiē shì mántou.', 'C. 不喝，我喝茶. / Bù hē, wǒ hē chá.', 'D. 三个。 / Sān ge.', 'E. 我吃面条儿。 / Wǒ chī miàntiáor.'], 'text': '22. 你吃什么？ / Nǐ chī shénme?', 'correct': 'E', 'explanation': 'Hỏi ăn gì -> Trả lời ăn mì (我吃面条儿).'},
            {'id': 23, 'type': 'mc', 'options': ['A. 去食堂。 / Qù shítáng.', 'B. 这些是馒头。 / Zhèxiē shì mántou.', 'C. 不喝，我喝茶。 / Bù hē, wǒ hē chá.', 'D. 三个。 / Sān ge.', 'E. 我吃面条儿。 / Wǒ chī miàntiáor.'], 'text': '23. 你喝啤酒吗？ / Nǐ hē píjiǔ ma?', 'correct': 'C', 'explanation': 'Hỏi uống bia không -> Trả lời không uống, tôi uống trà (不喝，我喝茶).'},
            {'id': 24, 'type': 'mc', 'options': ['A. 去食堂。 / Qù shítáng.', 'B. 这些是馒头。 / Zhèxiē shì mántou.', 'C. 不喝，我喝茶。 / Bù hē, wǒ hē chá.', 'D. 三个。 / Sān ge.', 'E. 我吃面条儿。 / Wǒ chī miàntiáor.'], 'text': '24. 这些是什么？ / Zhèxiē shì shénme?', 'correct': 'B', 'explanation': 'Hỏi đây là những cái gì -> Trả lời đây là bánh màn thầu (这些是馒头).'},
            {'id': 25, 'type': 'mc', 'options': ['A. 去食堂。 / Qù shítáng.', 'B. 这些是馒头。 / Zhèxiē shì mántou.', 'C. 不喝，我喝茶。 / Bù hē, wǒ hē chá.', 'D. 三个。 / Sān ge.', 'E. 我吃面条儿。 / Wǒ chī miàntiáor.'], 'text': '25. 你要几个包子？ / Nǐ yào jǐ ge bāozi?', 'correct': 'D', 'explanation': 'Hỏi muốn mấy cái bánh bao -> Trả lời 3 cái (三个).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A. 汤 / tāng', 'B. 碗 / wǎn', 'C. 食堂 / shítáng', 'D. 名字 / míngzi', 'E. 请 / qǐng', 'F. 米饭 / mǐfàn'], 'text': '26. 明天中午我（  ）你吃饭。', 'correct': 'E', 'explanation': 'Chọn động từ "请" (mời) -> Mời bạn ăn cơm.'},
            {'id': 27, 'type': 'mc', 'options': ['A. 汤 / tāng', 'B. 碗 / wǎn', 'C. 食堂 / shítáng', 'D. 名字 / míngzi', 'E. 请 / qǐng', 'F. 米饭 / mǐfàn'], 'text': '27. 我不吃（  ），我吃面条儿。', 'correct': 'F', 'explanation': 'Chọn danh từ món ăn "米饭" (cơm) -> Không ăn cơm, ăn mì.'},
            {'id': 28, 'type': 'mc', 'options': ['A. 汤 / tāng', 'B. 碗 / wǎn', 'C. 食堂 / shítáng', 'D. 名字 / míngzi', 'E. 请 / qǐng', 'F. 米饭 / mǐfàn'], 'text': '28. 我要一（  ）面条儿，一个馒头。', 'correct': 'B', 'explanation': 'Chọn lượng từ "碗" (bát/tô) đi với mì.'},
            {'id': 29, 'type': 'mc', 'options': ['A. 汤 / tāng', 'B. 碗 / wǎn', 'C. 食堂 / shítáng', 'D. 名字 / míngzi', 'E. 请 / qǐng', 'F. 米饭 / mǐfàn'], 'text': '29. 女：你喝什么（  ）？ 男：我不喝（  ），我喝啤酒。', 'correct': 'A', 'explanation': 'Chọn từ "汤" (canh) -> Uống canh gì.'},
            {'id': 30, 'type': 'mc', 'options': ['A. 汤 / tāng', 'B. 碗 / wǎn', 'C. 食堂 / shítáng', 'D. 名字 / míngzi', 'E. 请 / qǐng', 'F. 米饭 / mǐfàn'], 'text': '30. 男：我们去哪儿吃饭？ 女：去（  ）吧。', 'correct': 'C', 'explanation': 'Điền danh từ địa điểm "食堂" (nhà ăn).'}
        ]
    },
    'bai_7': {
        'title': 'BÀI 7: TÔI HỌC TIẾNG HÁN / 我学习汉语',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai
            {'id': 1, 'type': 'tf', 'text': '1. 你好！/ Nǐhǎo!', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '你好！', 'explanation': 'Theo đáp án chính thức, câu này phán đoán là Sai (✗).'},
            {'id': 2, 'type': 'tf', 'text': '2. 再见 / Zàijiàn', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '再见', 'explanation': 'Theo đáp án chính thức, câu này phán đoán là Đúng (✓).'},
            {'id': 3, 'type': 'tf', 'text': '3. 学习汉语 / Xuéxí Hànyǔ', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '学习汉语', 'explanation': 'Theo đáp án chính thức, câu này phán đoán là Đúng (✓).'},
            {'id': 4, 'type': 'tf', 'text': '4. 老师 / Lǎoshī', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '老师', 'explanation': 'Theo đáp án chính thức, câu này phán đoán là Sai (✗).'},
            {'id': 5, 'type': 'tf', 'text': '5. 很好 / Hěn hǎo', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '很好', 'explanation': 'Theo đáp án chính thức, câu này phán đoán là Đúng (✓).'},
            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '6. ', 'audio_part': 2, 'correct': 'D', 'script': '男：这本书是谁的？\n女：是王老师的。', 'explanation': 'Đối thoại nói về quyển sách (书), tương ứng hình D.'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '7. ', 'audio_part': 2, 'correct': 'A', 'script': '女：你一个人去中国？\n男：不，和我爸妈，我们三个人。', 'explanation': 'Vali đi du lịch Trung Quốc cùng gia đình, khớp hình A.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '8. ', 'audio_part': 2, 'correct': 'F', 'script': '男：您好！您是美国人吗？\n男：是，我是美国人。', 'explanation': 'Bắt tay chào hỏi lịch sự giữa 2 quý ông người Mỹ, khớp hình F.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '9. ', 'audio_part': 2, 'correct': 'E', 'script': '男：她是哪国人？\n女：她是中国人。', 'explanation': 'Cô gái người Trung Quốc đang ăn cơm, khớp hình E.'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '10. ', 'audio_part': 2, 'correct': 'B', 'script': '女：老师，谢谢您，再见！\n男：再见！', 'explanation': 'Học sinh nữ chào tạm biệt thầy giáo, khớp hình B.'},
            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A. 李月 / Lǐ Yuè', 'B. 张东 / Zhāng Dōng', 'C. 玛丽 / Mǎlì'], 'text': '11. 她叫什么名字？', 'audio_part': 3, 'correct': 'A', 'script': '她叫李月，她是老师。\n问：她叫什么名字？', 'explanation': 'Tên cô ấy là "李月". Chọn A.'},
            {'id': 12, 'type': 'mc', 'options': ['A. 我的朋友 / wǒ de péngyou', 'B. 我的哥哥 / wǒ de gēge', 'C. 我的老师 / wǒ de lǎoshī'], 'text': '12. 他是谁？', 'audio_part': 3, 'correct': 'C', 'script': '他是中国人，他是我的汉语老师。\n问：他是谁？', 'explanation': 'Thầy ấy là giáo viên tiếng Hán của tôi (我的汉语老师). Chọn C.'},
            {'id': 13, 'type': 'mc', 'options': ['A. 星期一 / xīngqīyī', 'B. 星期六 / xīngqīliù', 'C. 星期天 / xīngqītiān'], 'text': '13. 明天星期几？', 'audio_part': 3, 'correct': 'C', 'script': '今天是星期天，我们明天回家。\n问：明天星期几？', 'explanation': 'Barem đáp án chính thức ghi nhận là C.'},
            {'id': 14, 'type': 'mc', 'options': ['A. 5天 / wǔ tiān', 'B. 3天 / sān tiān', 'C. 7天 / qī tiān'], 'text': '14. 他们一个星期学习几天？', 'audio_part': 3, 'correct': 'A', 'script': '我和朋友来中国学习汉语，我们一個星期学习五天。\n问：他们一个星期学习几天？', 'explanation': 'Học năm ngày (五天). Chọn A.'},
            {'id': 15, 'type': 'mc', 'options': ['A. 喝咖啡 / hē kāfēi', 'B. 学习 / xuéxí', 'C. 去公园 / qù gōngyuán'], 'text': '15. 他在这儿做什么？', 'audio_part': 3, 'correct': 'B', 'script': '我不是北京人，我在这儿学习。\n问：他在这儿做什么？', 'explanation': 'Học tập ở đây (学习). Chọn B.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình đúng sai
            {'id': 16, 'type': 'tf', 'text': '16. Hànzì / 汉字', 'correct': 'Sai (✗)', 'explanation': 'Chữ viết trên bảng là chữ cái tiếng Anh, không phải chữ Hán.'},
            {'id': 17, 'type': 'tf', 'text': '17. xīngqīyī / 星期一', 'correct': 'Đúng (✓)', 'explanation': 'Monday chính là Thứ Hai.'},
            {'id': 18, 'type': 'tf', 'text': '18. xuéxiào / 学校', 'correct': 'Sai (✗)', 'explanation': 'Theo đáp án chuẩn gốc, câu này là Sai (✗).'},
            {'id': 19, 'type': 'tf', 'text': '19. qǐng zuò / 请坐', 'correct': 'Đúng (✓)', 'explanation': 'Ghế kéo ra mời ngồi khớp với "请坐".'},
            {'id': 20, 'type': 'tf', 'text': '20. xuéxí / 学习', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh đọc sách ôn bài.'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A. 她叫玛丽。 / Tā jiào Mǎlì.', 'B. 他是我的朋友。 / Tā shì wǒ de péngyou.', 'C. 他是法国人。 / Tā shì Fǎguó rén.', 'D. 我姓王。 / Wǒ xìng Wáng.', 'E. 我学习英语。 / Wǒ xuéxí Yīngyǔ.'], 'text': '21. 他是哪国人？ / Tā shì nǎ guó rén?', 'correct': 'C', 'explanation': 'Hỏi quốc tịch anh ấy -> Anh ấy là người Pháp (法国人).'},
            {'id': 22, 'type': 'mc', 'options': ['A. 她叫玛丽。 / Tā jiào Mǎlì.', 'B. 他es我的朋友。 / Tā shì wǒ de péngyou.', 'C. 他es法国人。 / Tā shì Fǎguó rén.', 'D. 我姓王。 / Wǒ xìng Wáng.', 'E. 我学习英语。 / Wǒ xuéxí Yīngyǔ.'], 'text': '22. 她叫什么名字？ / Tā jiào shénme míngzi?', 'correct': 'A', 'explanation': 'Hỏi tên cô ấy -> Cô ấy tên Mary (玛丽).'},
            {'id': 23, 'type': 'mc', 'options': ['A. 她叫玛丽。 / Tā jiào Mǎlì.', 'B. 他es我的朋友。 / Tā shì wǒ de péngyou.', 'C. 他es法国人。 / Tā shì Fǎguó rén.', 'D. 我姓王。 / Wǒ xìng Wáng.', 'E. 我学习英语。 / Wǒ xuéxí Yīngyǔ.'], 'text': '23. 你学习什么？ / Nǐ xuéxí shénme?', 'correct': 'E', 'explanation': 'Hỏi bạn học gì -> Tôi học tiếng Anh (英语).'},
            {'id': 24, 'type': 'mc', 'options': ['A. 她叫玛丽。 / Tā jiào Mǎlì.', 'B. 他es我的朋友。 / Tā shì wǒ de péngyou.', 'C. 他es法国人。 / Tā shì Fǎguó rén.', 'D. 我姓王。 / Wǒ xìng Wáng.', 'E. 我学习英语。 / Wǒ xuéxí Yīngyǔ.'], 'text': '24. 他是谁？ / Tā shì shuí?', 'correct': 'B', 'explanation': 'Hỏi anh ấy là ai -> Anh ấy là bạn tôi (我的朋友).'},
            {'id': 25, 'type': 'mc', 'options': ['A. 她叫玛丽。 / Tā jiào Mǎlì.', 'B. 他es我的朋友。 / Tā shì wǒ de péngyou.', 'C. 他es法国人。 / Tā shì Fǎguó rén.', 'D. 我姓王。 / Wǒ xìng Wáng.', 'E. 我学习英语。 / Wǒ xuéxí Yīngyǔ.'], 'text': '25. 请问，您贵姓？ / Qǐngwèn, nín guìxìng?', 'correct': 'D', 'explanation': 'Hỏi họ lịch sự -> Tôi họ Vương (姓王).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A. 叫 / jiào', 'B. 太 / tài', 'C. 美国 / Měiguó', 'D. 名字 / míngzi', 'E. 的 / de', 'F. 学校 / xuéxiào'], 'text': '26. 我学习汉语，汉语不（  ）难。', 'correct': 'B', 'explanation': 'Tiếng Hán không khó lắm (不太难).'},
            {'id': 27, 'type': 'mc', 'options': ['A. 叫 / jiào', 'B. 太 / tài', 'C. 美国 / Měiguó', 'D. 名字 / míngzi', 'E. 的 / de', 'F. 学校 / xuéxiào'], 'text': '27. 他是我的朋友，他是（  ）人。', 'correct': 'C', 'explanation': 'Anh ấy là người Mỹ (美国人).'},
            {'id': 28, 'type': 'mc', 'options': ['A. 叫 / jiào', 'B. 太 / tài', 'C. 美国 / Měiguó', 'D. 名字 / míngzi', 'E. 的 / de', 'F. 学校 / xuéxiào'], 'text': '28. 这是张老师，我（  ）汉语老师。', 'correct': 'E', 'explanation': 'Điền "的" -> Giáo viên tiếng Hán của tôi.'},
            {'id': 29, 'type': 'mc', 'options': ['A. 叫 / jiào', 'B. 太 / tài', 'C. 美国 / Měiguó', 'D. 名字 / míngzi', 'E. 的 / de', 'F. 学校 / xuéxiào'], 'text': '29. 女：你（  ）什么名字？ 男：我叫张东。', 'correct': 'A', 'explanation': 'Hỏi tên dùng động từ "叫".'},
            {'id': 30, 'type': 'mc', 'options': ['A. 叫 / jiào', 'B. 太 / tài', 'C. 美国 / Měiguó', 'D. 名字 / míngzi', 'E. 的 / de', 'F. 学校 / xuéxiào'], 'text': '30. 男：明天你去公园吗？ 女：不去, 我去（  ）。', 'correct': 'F', 'explanation': 'Điền "学校" -> Tôi đến trường.'}
        ]
    },
    'bai_6': {
        'title': 'BÀI 6: ĐÂY LÀ THẦY GIÁO VƯƠNG (BÀI ÔN TẬP 1) / 这是王老师 (复习一)',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai
            {'id': 1, 'type': 'tf', 'text': '1. 明天见 / Míngtiān jiàn', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '明天见', 'explanation': 'Học sinh đi học về chào nhau tạm biệt ngày mai.'},
            {'id': 2, 'type': 'tf', 'text': '2. 星期六 / Xīngqīliù', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '星期六', 'explanation': 'Hình ảnh hiển thị "Sunday" (Chủ Nhật).'},
            {'id': 3, 'type': 'tf', 'text': '3. 喝茶 / Hē chá', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '喝茶', 'explanation': 'Cô gái đang uống nước lọc thường, đáp án chính thức là Sai.'},
            {'id': 4, 'type': 'tf', 'text': '4. 去公园 / Qù gōngyuán', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '去公园', 'explanation': 'Người phụ nữ đang đi siêu thị mua hàng.'},
            {'id': 5, 'type': 'tf', 'text': '5. 三个人 / Sān gè rén', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '三个人', 'explanation': 'Hình ảnh có chính xác 3 học sinh đang học bài.'},
            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '6. ', 'audio_part': 2, 'correct': 'F', 'script': '男：今天星期几？\n女：今天星期三。', 'explanation': 'Hỏi thứ mấy -> Hôm nay là thứ Tư (Hình F).'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '7. ', 'audio_part': 2, 'correct': 'A', 'script': '男：妈，我去学校了。再见！\n女：好，再见！', 'explanation': 'Học sinh chào tạm biệt mẹ đi học, khớp hình A.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '8. ', 'audio_part': 2, 'correct': 'B', 'script': '女：您好，您想喝点儿什么？\n男：一杯茶，谢谢。', 'explanation': 'Gọi nước và lấy trà, khớp hình B.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '9. ', 'audio_part': 2, 'correct': 'D', 'script': '男：她是谁？\n女：她是我的汉语老师。', 'explanation': 'Giới thiệu giáo viên tiếng Hán (Hình D).'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': '10. ', 'audio_part': 2, 'correct': 'E', 'script': '男：这两个人是谁？\n女：这是我爸爸和妈妈。', 'explanation': 'Giới thiệu bố mẹ, khớp hình E.'},
            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A. 星期五 / xīngqīwǔ', 'B. 星期六 / xīngqīliù', 'C. 星期天 / xīngqītiān'], 'text': '11. 今天星期几？', 'audio_part': 3, 'correct': 'C', 'script': '明天星期一，我去学校。\n问：今天星期几？', 'explanation': 'Ngày mai là Thứ Hai -> Hôm nay là Chủ Nhật (星期天). Chọn C.'},
            {'id': 12, 'type': 'mc', 'options': ['A. 李红 / Lǐ Hóng', 'B. 他的老师 / tā de lǎoshī', 'C. 李红的妈妈 / Lǐ Hóng de māma'], 'text': '12. 那个人是谁？', 'audio_part': 3, 'correct': 'B', 'script': '这个人不是李红的妈妈，她是我的老师。\n问：那个人是谁？', 'explanation': 'Không phải mẹ Lý Hồng, đó là giáo viên của tôi (我的老师). Chọn B.'},
            {'id': 13, 'type': 'mc', 'options': ['A. 学校 / xuéxiào', 'B. 公园 / gōngyuán', 'C. 银行 / yínháng'], 'text': '13. 他们明天在哪儿见面？', 'audio_part': 3, 'correct': 'A', 'script': '我们明天在学校见面。\n问：他们明天在哪儿见面？', 'explanation': 'Gặp nhau ở trường học (学校). Chọn A.'},
            {'id': 14, 'type': 'mc', 'options': ['A. 他爸爸 / tā bàba', 'B. 他朋友 / tā péngyou', 'C. 他的老师 / tā de lǎoshī'], 'text': '14. 谁是老师？', 'audio_part': 3, 'correct': 'B', 'script': '这是我朋友，她是小学老师。\n问：谁是老师？', 'explanation': 'Bạn tôi là giáo viên tiểu học. Chọn B.'},
            {'id': 15, 'type': 'mc', 'options': ['A. 茶 / chá', 'B. 咖啡 / kāfēi', 'C. 水 / shuǐ'], 'text': '15. 他想喝什么？', 'audio_part': 3, 'correct': 'A', 'script': '他想喝茶，你呢？\n问：他想喝什么？', 'explanation': 'Anh ấy muốn uống trà (想喝茶). Chọn A.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình đúng sai
            {'id': 16, 'type': 'tf', 'text': '16. kāfēi / 咖啡', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh tách cà phê nóng.'},
            {'id': 17, 'type': 'tf', 'text': '17. qù / 去', 'correct': 'Sai (✗)', 'explanation': 'Hình ảnh ngồi ghế tựa thư giãn, không biểu thị hành động "去".'},
            {'id': 18, 'type': 'tf', 'text': '18. sān / 三', 'correct': 'Đúng (✓)', 'explanation': 'Có chính xác 3 quả táo.'},
            {'id': 19, 'type': 'tf', 'text': '19. zàijiàn / 再见', 'correct': 'Sai (✗)', 'explanation': 'Hình ảnh bắt tay chào nhau khi mới gặp, không biểu thị "再见".'},
            {'id': 20, 'type': 'tf', 'text': '20. shū / 书', 'correct': 'Đúng (✓)', 'explanation': 'Quyển sách dày dặn.'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A. 我去邮局。 / Wǒ qù yóujú.', 'B. 这是英文杂志。 / Zhè shì Yīngwén zázhì.', 'C. 今天星期四。 / Jīntiān xīngqīsì.', 'D. 我喝咖啡。 / Wǒ hē kāfēi.', 'E. 那是我妈妈的书。 / Nà shì wǒ māma de shū.'], 'text': '21. 你喝点儿什么？ / Nǐ hē diǎnr shénme?', 'correct': 'D', 'explanation': 'Tôi uống cà phê (我喝咖啡).'},
            {'id': 22, 'type': 'mc', 'options': ['A. 我去邮局。 / Wǒ qù yóujú.', 'B. 这是英文杂志。 / Zhè shì Yīngwén zázhì.', 'C. 今天星期四。 / Jīntiān xīngqīsì.', 'D. 我喝咖啡。 / Wǒ hē kāfēi.', 'E. 那是我妈妈的书。 / Nà shì wǒ māma de shū.'], 'text': '22. 你去哪儿？ / Nǐ qù nǎr?', 'correct': 'A', 'explanation': 'Tôi đi bưu điện (我去邮局).'},
            {'id': 23, 'type': 'mc', 'options': ['A. 我去邮局。 / Wǒ qù yóujú.', 'B. 这是英文杂志。 / Zhè shì Yīngwén zázhì.', 'C. 今天星期四。 / Jīntiān xīngqīsì.', 'D. 我喝咖啡。 / Wǒ hē kāfēi.', 'E. 那是我妈妈的书。 / Nà shì wǒ māma de shū.'], 'text': '23. 这是什么杂志？ / Zhè shì shénme zázhì?', 'correct': 'B', 'explanation': 'Đây là tạp chí tiếng Anh (这是英文杂志).'},
            {'id': 24, 'type': 'mc', 'options': ['A. 我去邮局。 / Wǒ qù yóujú.', 'B. 这是英文杂志。 / Zhè shì Yīngwén zázhì.', 'C. 今天星期四。 / Jīntiān xīngqīsì.', 'D. 我喝咖啡。 / Wǒ hē kāfēi.', 'E. 那是我妈妈的书。 / Nà shì wǒ māma de shū.'], 'text': '24. 今天星期几？ / Jīntiān xīngqī jǐ?', 'correct': 'C', 'explanation': 'Hôm nay là Thứ Năm (今天星期四).'},
            {'id': 25, 'type': 'mc', 'options': ['A. 我去邮局。 / Wǒ qù yóujú.', 'B. 这是英文杂志。 / Zhè shì Yīngwén zázhì.', 'C. 今天星期 ấm. / Jīntiān xīngqīsì.', 'D. 我喝咖啡。 / Wǒ hē kāfēi.', 'E. 那是我妈妈的书。 / Nà shì wǒ māma de shū.'], 'text': '25. 那是谁的书？ / Nà shì shuí de shū?', 'correct': 'E', 'explanation': 'Đó là sách của mẹ tôi (那是我妈妈的书).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A. 忙 / máng', 'B. 谁 / shuí', 'C. 学校 / xuéxiào', 'D. 名字 / míngzi', 'E. 进 / jìn', 'F. 星期天 / xīngqītiān'], 'text': '26. 这是（  ）的信？', 'correct': 'B', 'explanation': 'Thư của ai (谁的信).'},
            {'id': 27, 'type': 'mc', 'options': ['A. 忙 / máng', 'B. 谁 / shuí', 'C. 学校 / xuéxiào', 'D. 名字 / míngzi', 'E. 进 / jìn', 'F. 星期天 / xīngqītiān'], 'text': '27. 我妈妈是老师, 她很（  ）。', 'correct': 'A', 'explanation': 'Mẹ rất bận (很忙).'},
            {'id': 28, 'type': 'mc', 'options': ['A. 忙 / máng', 'B. 谁 / shuí', 'C. 学校 / xuéxiào', 'D. 名字 / míngzi', 'E. 进 / jìn', 'F. 星期天 / xīngqītiān'], 'text': '28. 昨天（  ）, 我去公园。', 'correct': 'F', 'explanation': 'Hôm qua là Chủ Nhật (昨天星期天).'},
            {'id': 29, 'type': 'mc', 'options': ['A. 忙 / máng', 'B. 谁 / shuí', 'C. 学校 / xuéxiào', 'D. 名字 / míngzi', 'E. 进 / jìn', 'F. 星期天 / xīngqītiān'], 'text': '29. 女：你去哪儿？ | 男：我去（  ）。', 'correct': 'C', 'explanation': 'Tôi đến trường (我去学校).'},
            {'id': 30, 'type': 'mc', 'options': ['A. 忙 / máng', 'B. 谁 / shuí', 'C. 学校 / xuéxiào', 'D. 名字 / míngzi', 'E. 进 / jìn', 'F. 星期天 / xīngqītiān'], 'text': '30. 男：你好！请（  ）！| 女：你的信。', 'correct': 'E', 'explanation': 'Xin mời vào (请进).'}
        ]
    }
}

# ==========================================================
# 3. TIÊU ĐỀ CHÍNH & PHẦN GIAO DIỆN CHUNG
# ==========================================================
st.markdown("<h1 class='main-title'>BÀI TẬP GIÁO TRÌNH HÁN NGỮ (1)</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Chúc các bạn làm bài vui và hiệu quả nha!</h3>", unsafe_allow_html=True)

# Định nghĩa hàm callback đồng bộ tên học sinh cực kỳ ổn định và chống lỗi gửi bài
def sync_student_name(lesson_id):
    key = f"name_input_{lesson_id}"
    val = st.session_state[key].strip()
    st.session_state["student_name"] = val
    for l_id in ['bai_8', 'bai_7', 'bai_6']:
        st.session_state[f"name_input_{l_id}"] = val

# Khởi tạo student_name trong session_state
if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""

# Đảm bảo các ô nhập tên được khởi tạo sẵn trong session_state
for l_id in ['bai_8', 'bai_7', 'bai_6']:
    if f"name_input_{l_id}" not in st.session_state:
        st.session_state[f"name_input_{l_id}"] = ""

student_name = st.session_state["student_name"]

# Thiết lập tabs: Bài mới nhất luôn ở bên trái ngoài cùng (Bài 8 -> Bài 7 -> Bài 6)
tabs = st.tabs(["📚 BÀI 8", "📚 BÀI 7", "📚 BÀI 6"])

lessons_mapping = [('bai_8', tabs[0]), ('bai_7', tabs[1]), ('bai_6', tabs[2])]

# Khởi tạo các biến session state cho từng bài học nếu chưa tồn tại
for l_id in ['bai_8', 'bai_7', 'bai_6']:
    if f"submitted_{l_id}" not in st.session_state:
        st.session_state[f"submitted_{l_id}"] = False
    if f"scores_{l_id}" not in st.session_state:
        st.session_state[f"scores_{l_id}"] = None

# HTML/JS for confetti fireworks on 30/30 score
confetti_html = """
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>
    var duration = 6 * 1000;
    var animationEnd = Date.now() + duration;
    var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min, max) {
      return Math.random() * (max - min) + min;
    }

    var interval = setInterval(function() {
      var timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      var particleCount = 50 * (timeLeft / duration);
      // launch from two corners
      confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
      confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
    }, 250);
</script>
"""

for lesson_id, tab in lessons_mapping:
    with tab:
        lesson_data = QUESTIONS[lesson_id]
        st.markdown(f"<div class='lesson-banner'>{lesson_data['title']}</div>", unsafe_allow_html=True)
        
        # Đồng bộ ô nhập tên học sinh trên từng bộ đề tự động sử dụng callback 100% ổn định
        student_name = st.text_input(
            "📝 Nhập Họ và tên của bạn để làm bài tập:",
            key=f"name_input_{lesson_id}",
            on_change=sync_student_name,
            args=(lesson_id,),
            disabled=st.session_state.get(f"submitted_{lesson_id}", False)
        )
        
        # Biến trạng thái nộp bài của bài cụ thể
        is_submitted = st.session_state[f"submitted_{lesson_id}"]
        scores = st.session_state[f"scores_{lesson_id}"]
        
        # --------------------------------------------------
        # A. PHẦN NGHE (15 CÂU)
        # --------------------------------------------------
        st.subheader("I. 听力 / PHẦN NGHE (15 câu)")
        
        # Audio cho Phần 1 (Câu 1-5)
        st.markdown("**🔊 Phần 1 (Câu 1 - 5):** Nghe từ/ngữ và phán đoán đúng (✓) / sai (✗)")
        audio_file_1 = f"B{lesson_id.split('_')[1]}-1.mp3"
        try:
            st.audio(audio_file_1, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_1} trong thư mục. Vui lòng thêm file để học sinh nghe.")
        
        for q in lesson_data['listening'][0:5]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown(f"<div class='quiz-card'>", unsafe_allow_html=True)
            
            # Hiển thị hình ảnh minh họa cho câu nghe 1 nếu có sẵn tệp ảnh trong thư mục
            img_path = f"B{lesson_id.split('_')[1]}_{q['id']}.png"
            if os.path.exists(img_path):
                st.image(img_path, width=220)
            else:
                st.info(f"💡 [Gợi ý giáo viên]: Thêm ảnh đặt tên là '{img_path}' vào thư mục để hiển thị hình câu này.")
                
            st.markdown(f"**{q['id']}.**")
            
            selected_option = st.radio(
                "Lựa chọn của bạn:",
                ["Chưa chọn", "Đúng (✓)", "Sai (✗)"],
                index=["Chưa chọn", "Đúng (✓)", "Sai (✗)"].index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Audio cho Phần 2 (Câu 6-10)
        st.markdown("**🔊 Phần 2 (Câu 6 - 10):** Nghe hội thoại và ghép hình")
        audio_file_2 = f"B{lesson_id.split('_')[1]}-2.mp3"
        try:
            st.audio(audio_file_2, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_2} trong thư mục.")
            
        # Hiển thị tất cả 6 hình ảnh lựa chọn (A-F) một lần duy nhất nằm ngang để học sinh đối chiếu
        st.markdown("**🖼️ Hình ảnh lựa chọn (A - F):**")
        cols = st.columns(6)
        img_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        for idx, letter in enumerate(img_letters):
            with cols[idx]:
                img_path = f"B{lesson_id.split('_')[1]}_{letter}.png"
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"Hình {letter}", use_container_width=True)
                else:
                    st.info(f"💡 Ảnh {letter} ({img_path})")

        for q in lesson_data['listening'][5:10]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['id']}.**") # In đậm cực kì ngắn gọn
            
            selected_option = st.selectbox(
                "Nối với hình (A - F):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Audio cho Phần 3 (Câu 11-15)
        st.markdown("**🔊 Phần 3 (Câu 11 - 15):** Nghe câu hỏi và chọn đáp án chính xác")
        audio_file_3 = f"B{lesson_id.split('_')[1]}-3.mp3"
        try:
            st.audio(audio_file_3, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_3} trong thư mục.")
            
        for q in lesson_data['listening'][10:15]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['id']}.**") # In đậm câu hỏi
            
            selected_option = st.radio(
                "Chọn đáp án đúng (A/B/C):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                # Check if starts with correct letter (e.g. "C. 米饭 / mǐfàn" starts with "C")
                is_correct = selected_option.startswith(q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # --------------------------------------------------
        # B. PHẦN ĐỌC (15 CÂU)
        # --------------------------------------------------
        st.subheader("II. 阅读 / PHẦN ĐỌC (15 câu)")
        
        # Phần Đọc 1 (Câu 16-20)
        st.markdown("**📖 Phần 1 (Câu 16 - 20):** Xem từ ngữ và phán đoán đúng (✓) / sai (✗)")
        for q in lesson_data['reading'][0:5]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            
            # Hiển thị hình ảnh minh họa cho câu hỏi nếu có sẵn tệp ảnh trong thư mục
            img_question_name = f"B{lesson_id.split('_')[1]}_{q['id']}.png"
            if os.path.exists(img_question_name):
                st.image(img_question_name, width=220)
            else:
                st.info(f"💡 [Gợi ý giáo viên]: Thêm ảnh đặt tên là '{img_question_name}' vào thư mục để hiển thị hình câu này.")
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**") # In đậm câu hỏi
            
            selected_option = st.radio(
                "Lựa chọn của bạn:",
                ["Chưa chọn", "Đúng (✓)", "Sai (✗)"],
                index=["Chưa chọn", "Đúng (✓)", "Sai (✗)"].index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Phần Đọc 2 (Câu 21-25)
        st.markdown("**📖 Phần 2 (Câu 21 - 25):** Phối hợp câu hỏi và câu trả lời")
        for q in lesson_data['reading'][5:10]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**") # In đậm câu hỏi
            
            selected_option = st.selectbox(
                "Nối đáp án đúng:",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = selected_option.startswith(q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Phần Đọc 3 (Câu 26-30)
        st.markdown("**📖 Phần 3 (Câu 26 - 30):** Điền từ thích hợp vào khoảng trống")
        
        # HIỂN THỊ KHUNG TỪ VỰNG CHỈ 1 LẦN DUY NHẤT Ở ĐẦU PHẦN 3
        word_bank_list = lesson_data['reading'][10]['options']
        word_bank_html = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join([f"<span style='color: #2E7D32; font-weight: bold; font-size: 17px;'>{item}</span>" for item in word_bank_list])
        st.markdown(f"""
        <div style="background-color: #E8F5E9; padding: 15px; border-radius: 12px; border: 1px solid #C8E6C9; text-align: center; margin-bottom: 25px;">
            {word_bank_html}
        </div>
        """, unsafe_allow_html=True)

        for q in lesson_data['reading'][10:15]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**") # In đậm câu hỏi
            
            selected_option = st.selectbox(
                "Chọn từ điền trống (A - F):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = selected_option.startswith(q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # --------------------------------------------------
        # C. NÚT NỘP BÀI & CHẤM ĐIỂM
        # --------------------------------------------------
        if not is_submitted:
            if st.button("📤 Nộp Bài Tập", key=f"submit_btn_{lesson_id}"):
                # Luôn lấy giá trị tên từ nguồn session_state chuẩn để tránh lỗi mất trạng thái
                current_student_name = st.session_state.get("student_name", "").strip()
                if not current_student_name:
                    st.error("⚠️ Bạn vui lòng nhập Họ và tên ở đầu trang trước khi nộp bài nhé!")
                else:
                    # Chấm điểm
                    listening_score = 0
                    for q in lesson_data['listening']:
                        ans = st.session_state.get(f"ans_{lesson_id}_{q['id']}", "Chưa chọn")
                        if ans != "Chưa chọn" and ans.startswith(q['correct']):
                            listening_score += 1
                            
                    reading_score = 0
                    for q in lesson_data['reading']:
                        ans = st.session_state.get(f"ans_{lesson_id}_{q['id']}", "Chưa chọn")
                        if ans != "Chưa chọn" and ans.startswith(q['correct']):
                            reading_score += 1
                            
                    total_score = listening_score + reading_score
                    
                    # Lưu kết quả
                    st.session_state[f"scores_{lesson_id}"] = {
                        'listening': listening_score,
                        'reading': reading_score,
                        'total': total_score
                    }
                    st.session_state[f"submitted_{lesson_id}"] = True
                    
                    # Gửi webhook tới Google Sheet
                    now = datetime.datetime.now() + datetime.timedelta(hours=7) # Quy đổi múi giờ GMT+7
                    payload = {
                        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "student_name": current_student_name,
                        "lesson_title": lesson_data['title'],
                        "listening_score": f"{listening_score}/15",
                        "reading_score": f"{reading_score}/15",
                        "total_score": f"{total_score}/30"
                    }
                    
                    webhook_success = False
                    if WEBHOOK_URL and "YOUR_MACRO_ID" not in WEBHOOK_URL:
                        try:
                            res = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10)
                            if res.status_code == 200:
                                webhook_success = True
                        except Exception:
                            pass
                    
                    # Hiện kết quả thành công cho học sinh
                    st.success("🎉 Chúc mừng bạn đã làm xong bài tập nha! Điểm đã được gửi về cho cô Bảo Ngọc!")
                    st.balloons()
                    
                    # Hiển thị pháo hoa rực rỡ nếu đạt điểm tối đa
                    if total_score == 30:
                        st.markdown(confetti_html, unsafe_allow_html=True)
                    
                    if not webhook_success:
                        st.warning("⚠️ Hệ thống chưa đồng bộ được với Google Sheet, bạn vui lòng chụp màn hình kết quả này gửi cho cô nhé!")
                        
                    # Rerun để hiển thị chi tiết đáp án và giải thích
                    st.rerun()
        else:
            # Đã nộp bài, hiển thị bảng điểm của học sinh
            st.markdown("### 📊 KẾT QUẢ BÀI LÀM CỦA BẠN")
            st.markdown(f"👤 **Học sinh**: `{st.session_state.get('student_name', '')}`")
            st.markdown(f"🎧 **Điểm phần nghe**: `{scores['listening']}/15`")
            st.markdown(f"📖 **Điểm phần đọc**: `{scores['reading']}/15`")
            st.markdown(f"🏆 **Tổng điểm đạt được**: `{scores['total']}/30`")
            
            if scores['total'] == 30:
                st.markdown(confetti_html, unsafe_allow_html=True)
                st.success("🌟 Tuyệt vời! Bạn đã đạt điểm tuyệt đối 30/30! 🌟")
            elif scores['total'] >= 25:
                st.success("👏 Rất tốt! Cố gắng phát huy nhé!")
            elif scores['total'] >= 15:
                st.info("👍 Bạn đã đạt yêu cầu. Luyện tập thêm để đạt điểm cao hơn nhé!")
            else:
                st.warning("💪 Cố lên nhé! Đọc kỹ giải thích và luyện tập lại để nâng cao kết quả nhé!")
                
            if st.button("🔄 Làm lại bài tập này", key=f"retry_{lesson_id}"):
                st.session_state[f"submitted_{lesson_id}"] = False
                st.session_state[f"scores_{lesson_id}"] = None
                for q in lesson_data['listening'] + lesson_data['reading']:
                    st.session_state[f"ans_{lesson_id}_{q['id']}"] = "Chưa chọn"
                st.rerun()

# ==========================================================
# 5. FOOTER TRANG WEB
# ==========================================================
st.markdown("""
<div class='footer'>
    黄宝玉老师
</div>
""", unsafe_allow_html=True)
