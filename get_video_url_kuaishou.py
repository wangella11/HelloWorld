# coding: utf-8
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from get_logger import logger
from writeCookie import login_by_cookie


pv = 0


def open_chrome_browser():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(8)  # 最大等待时间
    return driver


# 登录
def login_and_search(driver, keyword):
    # 打开搜索页面
    url = "https://www.kuaishou.com/search/video?searchKey="+keyword
    driver.get(url)
    time.sleep(3)


def get_current_video_info(driver, video):
    video_data = {}
    # 在搜索页面，点击打开视频
    video.find_element(By.CLASS_NAME, "video-card-main").click()
    time.sleep(3)
    # 获取视频信息
    video_data["uploaderName"] = driver.find_element(By.CLASS_NAME,"profile-user-name-title").text
    video_data["releasTime"] = driver.find_element(By.CLASS_NAME, "photo-time").text
    video_data["videoLikes"] = driver.find_element(By.CLASS_NAME, "item-count").text
    video_data["videoPageUrl"] = driver.current_url
    # logger.info(f"当前视频信息:{video_data}")
    return video_data


def get_current_viedo_author_info(driver):
    user_data = {}
    # 在视频页面，点击作者头像
    driver.find_element(By.CLASS_NAME, "profile-user-name-title").click()
    time.sleep(2)
    # 获取作者信息
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    user_data["product_number"] = driver.find_element(By.XPATH, "//div[@class='user-detail-info']/div[1]/h3").text
    user_data["uploaderFans"] = driver.find_element(By.XPATH, "//div[@class='user-detail-info']/div[2]/h3").text
    user_data["uploaderFav"] = driver.find_element(By.XPATH, "//div[@class='user-detail-info']/div[3]/h3").text
    user_data["uploaderCI"] = driver.find_element(By.CLASS_NAME, "user-desc").text
    user_data["uploaderPage"] = driver.current_url
    # logger.info(f"当前up主信息:{user_data}")
    # 关闭当前用户窗口,返回前一个视频窗口
    driver.close()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    return user_data


def get_search_datas(driver):
    # 循环获取多页视频信息
    datas = []
    index = 0
    while True:
        # 获取当前页视频元素
        videos = driver.find_elements(By.CSS_SELECTOR, '.video-card.video-item')
        length = len(videos)
        logger.info(f"当前页面视频个数:{length}")
        # 如果页面元素没有增加则结束
        if length == index:
            logger.info(f'当前内容没有改变, 结束获取')
            break
        for temp in range(index, length):
            logger.info(f"第{temp}个视频")
            data = None
            # 获取视频的点赞量若过小 则结束
            likes = videos[temp].find_element(By.CLASS_NAME, "info-text").text
            # 去除喜欢
            if likes.find("喜欢"):
                likes = likes[:likes.find("喜欢")]
            # 点赞量单位转换
            if likes.count("万"):
                playnumber = int(float(likes[:-1]) * 10000)
            else:
                playnumber = int(likes)

            # 判断其值大小，不足指定值则不需获取信息，否则直接点击进去获取进一步信息
            if playnumber < pv:
                logger.info(f"点赞量：{playnumber}不足{pv}，不进行获取")
                continue
            else:
                # 获取视频信息
                data = get_current_video_info(driver, videos[temp])
                # 获取用户信息
                data.update(get_current_viedo_author_info(driver))
            # 关闭视频返回搜索页面
            driver.find_element(By.CLASS_NAME, "close-page").click()
            # 添加数据
            datas.append(data)
            index += 1
            # 打印
            logger.info(f'当前视频数据{data}')

        # 判断是否加载完
        if len(driver.find_elements(By.XPATH,"//div[contains(text(),'已经到底了，没有更多内容了')]"))<=0:
            logger.info("往下拖滚动条")
            driver.execute_script("arguments[0].scrollIntoView()",videos[-1])
            time.sleep(8)
        else:
            logger.info(f'当前搜索内容已加载完毕,结束获取')
            break
    return datas


def get_all_keywords_datas(filename):
    with open(filename) as f1:
        keywords = f1.readlines()
    datas = []
    for keyword in keywords:
        if keyword.endswith("\n"):
            keyword = keyword[:-1]
        print(keyword)
        datas.append(keyword)
    print(datas)
    return datas
    pass


def closeRoleDialog(driver):
    # 关闭它
    try:
        if len(driver.find_elements(By.XPATH, '//div[@role="dialog"]'))>0:
            driver.find_element(By.CLASS_NAME, "a.verify-bar-close").click()
            logger.info("弹出了手动点击确认框，准备关闭它！")
    except Exception as err:
        logger.info(f"没有弹出确认框或者关闭失败{err}")
    try:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.DOWN)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
    except Exception as err:
        logger.info(f"没有弹出遮罩层{err}")

if __name__ == '__main__':
    # # 获取数据
    driver = open_chrome_browser()
    login_and_search(driver, "IVE I AM")
    result = get_search_datas(driver)
    print(result)
    pass
