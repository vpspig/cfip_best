import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"网页获取失败: {str(e)}")
        return None

def parse_html(html, ip_type='ipv4'):
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 根据实际网页结构调整选择器
    table = soup.find('tbody')
    if not table:
        print("未找到数据表格！请检查网页结构")
        return []
    
    results = []
    for row in table.select('tr'):
        cols = row.find_all('td')
        if len(cols) < 6:
            continue
        
        # 提取各字段（根据实际列顺序调整）
        line_name = cols[0].text.strip()
        ip_address = cols[1].text.strip()
        data_center = cols[-2].text.strip()  # 假设数据中心在倒数第二列
        
        # 生成不同格式的输出
        if ip_type == 'ipv4':
            results.append(f"{ip_address} #{line_name}-{data_center}")
        else:  # ipv6
            results.append(f"{ip_address} #{line_name}-{data_center}")
    
    return results

def save_to_file(data, filename):
    if not data:
        print(f"无有效数据可保存到 {filename}")
        return
    
    # 去重并排序
    unique_data = sorted(set(data))
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(unique_data))
    
    print(f"成功保存 {len(unique_data)} 条数据到 {filename}")
    
    # 添加时间戳记录
    with open(f"{filename}.log", 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 采集到 {len(unique_data)} 条数据\n")

def main():
    # 创建命令行参数解析
    parser = argparse.ArgumentParser(description='采集Cloudflare IP地址')
    parser.add_argument('--type', choices=['ipv4', 'ipv6', 'all'], default='all',
                       help='指定采集类型: ipv4, ipv6, 或 all (默认)')
    parser.add_argument('--output', help='自定义输出文件名')
    
    args = parser.parse_args()
    
    # 定义URL和文件名映射
    configs = {
        'ipv4': {
            'url': 'https://www.wetest.vip/page/cloudflare/address_v4.html',
            'filename': args.output if args.output and args.type == 'ipv4' else 'ipv4.txt'
        },
        'ipv6': {
            'url': 'https://www.wetest.vip/page/cloudflare/address_v6.html',
            'filename': args.output if args.output and args.type == 'ipv6' else 'ipv6.txt'
        }
    }
    
    # 根据参数决定采集哪些类型
    types_to_collect = []
    if args.type == 'all':
        types_to_collect = ['ipv4', 'ipv6']
    else:
        types_to_collect = [args.type]
    
    all_data = {}
    
    for ip_type in types_to_collect:
        print(f"\n开始采集 {ip_type.upper()} 数据...")
        config = configs[ip_type]
        
        html = get_html(config['url'])
        if html:
            data = parse_html(html, ip_type)
            if data:
                all_data[ip_type] = data
                save_to_file(data, config['filename'])
            else:
                print(f"{ip_type.upper()} 无有效数据")
        else:
            print(f"{ip_type.upper()} 网页获取失败")
    
    # 如果采集了所有类型，可以生成合并文件
    if args.type == 'all' and len(all_data) == 2:
        combined_data = all_data['ipv4'] + all_data['ipv6']
        save_to_file(combined_data, 'ip_all.txt')
        print("\n已生成合并文件 ip_all.txt")

if __name__ == '__main__':
    main()
