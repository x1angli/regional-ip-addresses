# regional-ip-addresses

## Disclaimer / 声明
The information (including but not limited to: documentation, code, and data) under this repository is not provided for any specific purpose, and should not be relied upon. While the author aims to keep information under this repository current, it is provided "as is" and there are no responsibilities or warranties as to the accuracy, fitness, or authorativeness regarding this repository. The author will not be liable or responsible to any one for any loss or damage arising under or in connection with: use of, or inability to use, the information under this repository, regardless of the origins of such content.

本代码库的信息（包括但不限于代码、文档、数据）并不适于任何具体的作用，且不可被依赖。虽然作者致力于使代码库信息与时俱进，也只能按照“现状”提供之。作者并不为本代码库的准确性、适用性、权威性承担责任或提供担保。无论信息的出处，作者不会为使用或者无法使用本代码库下的信息所导致的损失损坏承担责任或法律责任。


## Introduction / 介绍

A Python script that generates regional IP addresses per CIDR notation. You import such IP addresses as whitelists into bypassing tools for full access of internet. 

本Python脚本用于生成CIDR格式的地区内的IP地址块。这些IP地址将可作为白名单被导入工具中，从而生成根据目标IP地址区域的路由表，最终目标是构建一个快速、无缝、相对稳定的上网工具。

## Intended Audience / 目标用户

This tool should be used by advanced users who has knowledge regarding networking and system administration. We assume our users are equipped with basic skills of setting up network-bypassing tools and routing table configuration. We recommend users with average IT proficiency use this tool under the guidance of your geek friends. Additionally, please keep in mind: __this tool is never intended to become any firewall-bypassing / IP disguising tool by itself.__

本工具的目标用户群体为具备网络和系统管理知识的高阶用户，且用户应当具备基本的穿越工具和路由表工具配置技能。对于那些普通用户，我们建议阁下在极客朋友的指导下使用本工具。请记住：__本工具本身不能被当作穿越工具或IP伪装工具__

## How it works / 工作原理

This tool would grab a list IP addresses from the [website of APNIC](http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest). Such list associates IP addresses with corresponding regions/countries. Then, it would parse the list, filters out IP addresses within a certain region, then converts it into [CIDR nodation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#CIDR_notation). After retrieving the set IP addresses inside a specified region, it would derive those IP addresses ourside that region by calculating the complement set. (Of course, those [reserved IP addresses](https://en.wikipedia.org/wiki/Reserved_IP_addresses) would also be excluded from the complement set.) Finally, both IP addresses inside region and the ones outside it would be written into a file, respectively. 

本工具将从[APNIC官网](http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest)抓取与国家或地区相对应的IP地址列表。在将IP列表进行解析，筛选出一个特定地区内的IP地址，并且转化为 [CIDR 格式](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#CIDR_notation). 在得到某一 __区内__ 的所有IP地址之后，本工具还将对其进行补集运算，以得到 __区外__ 的所有IP地址。（当然， [保留的IP 地址](https://en.wikipedia.org/wiki/Reserved_IP_addresses)会在补集中去除) 。最终，区内和区外的IP地址列表将分别写入文件中。


## Getting Started / 开始使用

### End users / 普通用户
You could simply download those files under the `output` folder under this repo, and use it as the "whitelist" for your :
* `output/CN-ipv4.txt` contains IPv4 addresses allocated to mainland China 
* `output/CN-ipv6.txt` contains IPv6 addresses allocated to mainland China 

直接调用本Github repo下的`output`文件夹下的文件，并将
* `output/CN-ipv4.txt` 包含墙内的IPv4地址
* `output/CN-ipv6.txt` 包含墙内的IPv6地址
* `output/outwall.txt` 包含墙外的IP地址；那些已经在RFC中被保留的地址已经被去除

### Advanced Users & Developers / 开发者
1. Make sure Python 3.6 or higher is properly installed.
2. `git clone` this project, or just download the .zip file from github.com and unarchive it, so as to make the project's base folder
3. Start CLI (DOS-like terminal, such as Command Prompt in Windows), enter the the project's base folder
4. Setup Python virtual environment with `virtualenv ...` or `python -m venv` ...
5. Run: `pip install -r requirements.txt`
6. Run: `python ipaddr.py`

... ... ... 

1. 确保系统上已经有Python 3.6 以上（抱歉，不支持Python 2.x）
2. `git clone` 本代码库
3. 在命令行中，进入本项目的文件夹目录
4. 设置并加载 venv / virtualenv
5. 运行 `pip install -r requirements.txt` 以加载requests等第三方模块
6. 运行 `python ipaddr.py`

## FAQ / 常见问答
#### 1. What's the benefit of using IP whitelists? / 使用IP地址的白名单有什么好处？
#### A: / 答: 
Everyone wants fast, smooth, reliable internet access. This is expecially crucial for expatriates, IT professionals, and scholars living in China. Currently, most firewall-bypassing tools unconditionally route all traffic through indirect channels (or contains outdated IP tables), which has side-effects such as low thoroughput, long latency, or even restrictions from IP-distinguishing music or video websites. This repo aims to provide an IP whitelist, which can be in turn used by firewall-bypassing tools capable of distinguishing destination, and therefore providing a better solution without such side-effects.

需要快速、平滑、可靠的网络连接，这对于外派人士、IT业者、学者们尤其至关重要。当代绝大多数的穿越工具会一股脑地接管所有网络流量，这会带来低吞吐、长延迟、甚至一些视听网站禁止访问的副作用。本代码库将提供一份IP白名单。

#### 2. How would you compare this tool with peers? / 与同类工具如何比较？
#### A: / 答: 
We are fully aware that there are some pieces of existing wheels that can achieve the task very well. For example, the one-line shell script below can generate the CIDR blocks for mainland China -- like a magic, huh? Yet we also believe that there are other features not covered by exisiting code -- The `outwall.txt`, IP addresses rest of the world, would be a perfect example.

我们十分清楚市面上有一些已经被发明的非常棒的轮子。比如下面的这个单行shell脚本就能像变魔术一样生成inwall.txt。但是我们相信别的工具还是存在死角。比如别的工具很难生成`outwall.txt`。

    curl 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest' | grep ipv4 | grep CN | awk -F\| '{ printf("%s/%d\n", $4, 32-log($5)/log(2)) }' > chnroute.txt

#### 3. After we obtain the output IP address blocks, so what? / 得到文件以后，我们能干什么
You can use tools such as [Shorewall] to edit the IP table of your OS. 

[Shorewall]:#user-content-shorewall "Shorewall"
> ##### Shorewall #####
> is an open source firewall tool for Linux that builds upon the Netfilter (iptables/ipchains) system built into the Linux kernel, making it easier to manage more complex configuration schemes by providing a higher level of abstraction for describing rules using text files."
> Official Website: http://shorewall.org
> Sourceforge: https://sourceforge.net/projects/shorewall/
> The most common two-interface example: http://shorewall.org/two-interface.htm

## Random Thoughts / 随笔
> “望长城内外，惟余莽莽；大河上下，顿失滔滔。”
> 
> 　　　　　　　　　　　———— 《沁园春·雪》
