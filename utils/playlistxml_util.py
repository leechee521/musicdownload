import xml.etree.ElementTree as ET
from datetime import datetime


def create_playlist_xml(playlist_name, song_paths, output_file):
    """
    创建歌单XML文件

    :param playlist_name: 歌单名称
    :param song_paths: 歌曲路径列表
    :param output_file: 输出XML文件路径
    """
    # 创建根元素Item
    item = ET.Element("Item")

    # 添加当前日期时间
    added = ET.SubElement(item, "Added")
    added.text = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    # 添加LockData
    lock_data = ET.SubElement(item, "LockData")
    lock_data.text = "false"

    # 添加LocalTitle
    local_title = ET.SubElement(item, "LocalTitle")
    local_title.text = playlist_name

    # 添加RunningTime
    running_time = ET.SubElement(item, "RunningTime")
    running_time.text = "5"  # 这里可以根据实际情况计算总时长

    # 添加OwnerUserId
    owner_id = ET.SubElement(item, "OwnerUserId")
    owner_id.text = "3346f37ba2a14518b2b8015d0982c7e3"  # 示例ID，可根据需要修改

    # 创建PlaylistItems
    playlist_items = ET.SubElement(item, "PlaylistItems")

    # 为每首歌曲添加PlaylistItem
    for path in song_paths:
        playlist_item = ET.SubElement(playlist_items, "PlaylistItem")
        path_element = ET.SubElement(playlist_item, "Path")
        path_element.text = path

    # 添加空的Shares元素
    shares = ET.SubElement(item, "Shares")

    # 添加PlaylistMediaType
    media_type = ET.SubElement(item, "PlaylistMediaType")
    media_type.text = "Audio"

    # 创建ElementTree并写入文件
    tree = ET.ElementTree(item)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


# 示例使用
if __name__ == "__main__":
    # 歌单名称
    playlist_name = "LOVE"

    # 歌曲路径列表
    song_paths = [
        "/media/qMusic/菲菲公主/Doll/Doll.flac",
        "/media/qMusic/Paula DeAnda/Why Would I Ever/Why Would I Ever.flac"
    ]

    # 输出文件路径
    output_file = "playlist.xml"

    # 创建歌单XML
    create_playlist_xml(playlist_name, song_paths, output_file)
    print(f"歌单XML文件已生成: {output_file}")