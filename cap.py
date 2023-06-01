import tkinter as tk
from tkinter import filedialog
import os
import cv2
import numpy as np

# 기본 설정값
default_transition_interval = 5
default_similarity_threshold = 0.99995

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_videos_in_folder(folder_path)

def process_videos_in_folder(folder_path):
    files = os.listdir(folder_path)

    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() in ['.mp4', '.avi', '.mov']:
            video_path = os.path.join(folder_path, file)
            process_video(video_path, folder_path)

def process_video(video_path, output_folder):
    # 동영상 파일 열기
    video = cv2.VideoCapture(video_path)

    # 이전 프레임
    prev_frame = None

    # 첫 번째 프레임 캡처 여부
    first_frame_captured = False

    # 영상 이름으로 폴더 생성
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_folder = os.path.join(output_folder, video_name)
    os.makedirs(video_folder, exist_ok=True)

    frame_count = 0

    # 이미지 유사도 측정을 위한 히스토그램 비교 함수
    def compare_histograms(hist1, hist2):
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    # 중복된 이미지 제거 함수
    def remove_duplicate_images(image_list):
        removed_indices = []
        num_images = len(image_list)

        for i in range(num_images):
            if i not in removed_indices:
                # 현재 이미지와 이후 이미지들을 비교하여 유사도가 높은 이미지 제거
                for j in range(i + 1, num_images):
                    if j not in removed_indices:
                        img1 = cv2.imread(image_list[i])
                        img2 = cv2.imread(image_list[j])

                        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
                        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])

                        similarity = compare_histograms(hist1, hist2)

                        if similarity > default_similarity_threshold:
                            print(similarity)
                            print(image_list[i])
                            print(image_list[j])
                            print(" ")
                            removed_indices.append(j)

        # 제거된 이미지 삭제
        for index in removed_indices:
            print(image_list[index])
            os.remove(image_list[index])

    image_list = []

    while True:
        ret, frame = video.read()

        if not ret:
            break

        if not first_frame_captured:
            capture_filename = os.path.join(video_folder, "0.png")
            cv2.imwrite(capture_filename, frame)
            image_list.append(capture_filename)
            print("첫 번째 프레임 캡처 완료:", capture_filename)
            first_frame_captured = True

        if prev_frame is not None:
            # 프레임 간의 차이 계산
            diff = cv2.absdiff(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))

            if cv2.mean(diff)[0] > 8:
                capture_filename = os.path.join(video_folder, "{}.png".format(frame_count))
                cv2.imwrite(capture_filename, frame)
                image_list.append(capture_filename)
                print("캡처 완료:", capture_filename)

        prev_frame = frame

        #프레임 건너뛰기
        video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + int(video.get(cv2.CAP_PROP_FPS) * default_transition_interval))

        frame_count += 1

    video.release()

    # 중복된 이미지 제거
    remove_duplicate_images(image_list)

def open_settings_window():
    settings_window = tk.Toplevel()
    settings_window.title("설정")

    # 창 위치 설정
    window_width = 300
    window_height = 200
    screen_width = settings_window.winfo_screenwidth()
    screen_height = settings_window.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 프레임 생성 및 가운데 정렬
    frame = tk.Frame(settings_window)
    frame.pack(expand=True, pady=20)

    # transition_interval 설정
    lbl_transition_interval = tk.Label(frame, text="탐색 간격 (초):", font=("맑은 고딕", 12))
    lbl_transition_interval.pack()

    entry_transition_interval = tk.Entry(frame, font=("Arial", 12))
    entry_transition_interval.insert(0, default_transition_interval)
    entry_transition_interval.pack()

    # similarity_threshold 설정
    lbl_similarity_threshold = tk.Label(frame, text="유사도 임계값:", font=("맑은 고딕", 12))
    lbl_similarity_threshold.pack()

    entry_similarity_threshold = tk.Entry(frame, font=("맑은 고딕", 12))
    entry_similarity_threshold.insert(0, default_similarity_threshold)
    entry_similarity_threshold.pack()

    # 확인 버튼
    btn_confirm = tk.Button(settings_window, text="확인", font=("맑은 고딕", 12), command=lambda: save_settings(entry_transition_interval.get(), entry_similarity_threshold.get(), settings_window))
    btn_confirm.pack(pady=20)

def save_settings(transition_interval, similarity_threshold, window):
    # 입력값 저장
    global default_transition_interval
    global default_similarity_threshold
    default_transition_interval = int(transition_interval) if transition_interval else default_transition_interval
    default_similarity_threshold = float(similarity_threshold) if similarity_threshold else default_similarity_threshold

    window.destroy()

window = tk.Tk()
window.title(string = "교안 캡쳐 자동화 도구")

# 창 위치 설정
window_width = 400
window_height = 300
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 프레임 생성 및 가운데 정렬
frame = tk.Frame(window)
frame.pack(expand=True)

button_select_folder = tk.Button(frame, text="폴더 선택", font=("맑은 고딕", 14), command=select_folder)
button_select_folder.pack(pady=20)

button_settings = tk.Button(frame, text="설정", font=("맑은 고딕", 14), command=open_settings_window)
button_settings.pack()

window.mainloop()
