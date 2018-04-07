# coding=utf-8
import os
import sys
import mosspy

if __name__ == '__main__':
    args = sys.argv[1:]
    language = args[0]
    result = args[1]
    submission = args[2]
    user_id = int(args[3])

    try:
        m = mosspy.Moss(user_id, language)
        m.options['m'] = 1000000
        for file in os.listdir(os.path.join(submission)):
            m.addFile(os.path.join(submission, file), file)
        url = m.send()
    except:
        os.mkdir(result)
        with open(os.path.join(result, 'index.html'), 'w') as fr:
            fr.write('''由于 moss 查重系统访问缓慢（可能被墙），此次查重失败。您可以新建一个查重并在另一个时间段重新尝试，或者使用 jplag 引擎''')
    else:
        os.mkdir(result)
        with open(os.path.join(result, 'index.html'), 'w') as fr:
            fr.write('''由于 moss 查重系统可能被墙，我们不提供静态的页面<br>
            请点击<a href='{0}'>此链接</a>以查看您的查重结果'''.format(url))
