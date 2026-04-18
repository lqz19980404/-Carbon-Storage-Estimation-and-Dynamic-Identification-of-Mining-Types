import numpy as np
import tifffile

def tiff_to_blocks(tiff_file, block_size=(5, 5), features=12):
    # 读取 TIFF 文件
    with tifffile.TiffFile(tiff_file) as tif:
        image = tif.asarray()  # 读取所有的图像数据

    # 将图像数据转换为 float32 类型
    image = image.astype(np.float32)

    # 将所有值为 -3.4028234663852886e+38 的值替换为 0
    image[image == -3.4028234663852886e+38] = 0

    # 获取图像的尺寸
    height, width = image.shape

    # 计算图像块的数量
    block_height, block_width = block_size
    num_blocks_y = height // block_height
    num_blocks_x = width // block_width

    # 创建一个空的数组来存储所有的图像块数据
    blocks = []

    # 循环遍历所有可能的块位置
    for i in range(num_blocks_y):
        for j in range(num_blocks_x):
            # 获取当前块的数据，形状为 (5, 5)
            block = image[i * block_height:(i + 1) * block_height, j * block_width:(j + 1) * block_width]

            # 每个图像块将会重复 12 次作为通道
            block_with_features = np.repeat(block[..., np.newaxis], features, axis=-1)

            blocks.append(block_with_features)

    # 将列表转换为 numpy 数组，最终形状为 (n, 5, 5, 12)
    blocks_array = np.array(blocks)

    return blocks_array


def save_data_as_npy(data, output_file):
    # 使用 numpy.save 将数据保存为 .npy 文件
    np.save(output_file, data)
    print(f"数据已成功保存到 {output_file}")


# 使用示例
tiff_file = r'G:\xlunwen\sy\3.impact_data\tiff8\2010/cropped_td2010.tif'  # 替换为实际的 TIFF 文件路径
output_file = r'G:\xlunwen\2010\TD/output_data.npy'  # 设置保存路径和文件名

# 获取生成的图像块数据
blocks_array = tiff_to_blocks(tiff_file)

# 保存数据到 .npy 文件
save_data_as_npy(blocks_array, output_file)

# 输出文件路径
print(f"数据保存完成：{output_file}")
