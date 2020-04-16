import cv2
import mail
import math
import numpy as np
from PIL import Image
import paddlehub as hub
from moviepy.editor import *

def getFrame(video_name, save_path):
    """
    将视频逐帧保存为图片
    :param video_name: 视频的名称
    :param save_path: 保存的路径
    :return:
    """
    video = cv2.VideoCapture(video_name)

    # 获取视频帧率
    fps = video.get(cv2.CAP_PROP_FPS)
    # 获取画面大小
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)

    # 获取帧数
    frame_num = str(video.get(7))
    name = int(math.pow(10, len(frame_num)))
    ret, frame = video.read()
    while ret:
        cv2.imwrite(save_path + str(name) + '.jpg', frame)
        ret, frame = video.read()
        name += 1
    video.release()
    return fps, size


def getHumanseg(frames):
    """
    对帧图片进行批量抠图
    :param frames: 帧的路径
    :return:
    """
    humanseg = hub.Module(name='deeplabv3p_xception65_humanseg')
    files = [frames + i for i in os.listdir(frames)]
    humanseg.segmentation(data={'image': files})  # 抠图

def setGreenBg(humanseg):
    """
    给抠好的图设置绿幕
    :param humanseg: 抠好的png图片
    :return: 返回图片的ndarray对象
    """
    im = Image.open(humanseg).convert('RGBA')
    # 遍历图片的每个像素
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            r, g, b, a = im.getpixel((i, j))
            if a == 0:
                im.putpixel((i, j), (0, 255, 0, 0))
    im = im.convert('RGB')
    im_array = np.array(im)
    im_array = im_array[:, :, ::-1]
    return im_array

def readBg(bgname, size):
    """
    读取背景图片，并修改尺寸
    :param bgname: 背景图片名称
    :param size: 视频分辨率
    :return: Image对象
    """
    im = Image.open(bgname)
    return im.resize(size)

def setImageBg(humanseg, bg_im):
    """
    将抠好的图和背景图片合并
    :param humanseg:
    :param bg_im:
    :return:
    """
    # 读取透明图片
    im = Image.open(humanseg)
    # 分离色道
    r, g, b, a = im.split()
    bg_im = bg_im.copy()
    bg_im.paste(im, (0, 0), mask=a)
    return np.array(bg_im.convert('RGB'))[:, :, ::-1]

def writeVideo(humanseg, bg_im, fps, size):
    """
    :param frames: 帧的路径
    :param bgname: 背景图片
    :param fps: 帧率
    :param size: 分辨率
    :return:
    """
    # 写入视频
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('green.mp4', fourcc, fps, size)

    # 将每一帧设置背景
    files = [humanseg + i for i in os.listdir(humanseg)]
    for file in files:
        im_array = setImageBg(file, bg_im)
        out.write(im_array)
    out.release()

def getMusic(video_name):
    """
    获取指定视频的音频
    :param video_name:
    :return:
    """
    # 读取视频文件
    video = VideoFileClip(video_name)
    # 返回音频
    return video.audio


def addMusic(video_name, audio):
    """实现混流，给video_name添加音频"""
    # 读取视频
    video = VideoFileClip(video_name)
    # 设置视频的音频
    video = video.set_audio(audio)
    # 保存新的视频文件
    video.write_videofile(output_video)


def deleteTransitionalFiles():
    """删除过渡文件"""
    frames = [frame_path + i for i in os.listdir(frame_path)]
    humansegs = [humanseg_path + i for i in os.listdir(humanseg_path)]
    for frame in frames:
        os.remove(frame)
    for humanseg in humansegs:
        os.remove(humanseg)

def changeVideoScene(video_name, bgname):
    """
    :param video_name: 视频的文件
    :param bgname: 背景图片
    :return:
    """

    # 读取视频中每一帧画面
    fps, size = getFrame(video_name, frame_path)

    # 批量抠图
    getHumanseg(frame_path)

    # 读取背景图片
    bg_im = readBg(bgname, size)

    # 将画面一帧帧写入视频
    writeVideo(humanseg_path, bg_im, fps, size)

    # 混流
    # addMusic('green.mp4', getMusic(video_name))

    # 删除过渡文件
    deleteTransitionalFiles()


if __name__ == '__main__':

    # 当前项目根目录
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    # 每一帧画面保存的地址
    frame_path = BASE_DIR + '\\frames\\'
    # 抠好的图片位置
    humanseg_path = BASE_DIR + '\\humanseg_output\\'
    # 最终视频的保存路径
    output_video = BASE_DIR + '\\result.mp4'

    if not os.path.exists(frame_path):
        os.makedirs(frame_path)

    try:
        changeVideoScene('jljt_m.mp4', 'bg.jpg')
        mail.sendMail('你的视频已经制作完成')
    except Exception as e:
        mail.sendMail('在制作过程中遇到了问题' + e.__str__())