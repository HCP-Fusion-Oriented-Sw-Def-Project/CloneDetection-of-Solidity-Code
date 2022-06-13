{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Encode result:00\n",
      "Decode result:3\n"
     ]
    }
   ],
   "source": [
    "#!/usr/bin/env python\n",
    "# -*- coding: utf-8 -*-\n",
    "\n",
    "\n",
    "# 统计字符出现频率，生成映射表\n",
    "def count_frequency(text):\n",
    "    chars = []\n",
    "    ret = []\n",
    "\n",
    "    for char in text:\n",
    "        if char in chars:\n",
    "            continue\n",
    "        else:\n",
    "            chars.append(char)\n",
    "            ret.append((char, text.count(char)))\n",
    "\n",
    "    return ret\n",
    "\n",
    "\n",
    "# 节点类\n",
    "class Node:\n",
    "    def __init__(self, frequency):\n",
    "        self.left = None\n",
    "        self.right = None\n",
    "        self.father = None\n",
    "        self.frequency = frequency\n",
    "\n",
    "    def is_left(self):\n",
    "        return self.father.left == self\n",
    "\n",
    "\n",
    "# 创建叶子节点\n",
    "def create_nodes(frequency_list):\n",
    "    return [Node(frequency) for frequency in frequency_list]\n",
    "\n",
    "\n",
    "# 创建Huffman树\n",
    "def create_huffman_tree(nodes):\n",
    "    queue = nodes[:]\n",
    "\n",
    "    while len(queue) > 1:\n",
    "        queue.sort(key=lambda item: item.frequency)\n",
    "        node_left = queue.pop(0)\n",
    "        node_right = queue.pop(0)\n",
    "        node_father = Node(node_left.frequency + node_right.frequency)\n",
    "        node_father.left = node_left\n",
    "        node_father.right = node_right\n",
    "        node_left.father = node_father\n",
    "        node_right.father = node_father\n",
    "        queue.append(node_father)\n",
    "\n",
    "    queue[0].father = None\n",
    "    return queue[0]\n",
    "\n",
    "\n",
    "# Huffman编码\n",
    "def huffman_encoding(nodes, root):\n",
    "    huffman_code = [''] * len(nodes)\n",
    "\n",
    "    for i in range(len(nodes)):\n",
    "        node = nodes[i]\n",
    "        while node != root:\n",
    "            if node.is_left():\n",
    "                huffman_code[i] = '0' + huffman_code[i]\n",
    "            else:\n",
    "                huffman_code[i] = '1' + huffman_code[i]\n",
    "            node = node.father\n",
    "\n",
    "    return huffman_code\n",
    "\n",
    "\n",
    "# 编码整个字符串\n",
    "def encode_str(text, char_frequency, codes):\n",
    "    ret = ''\n",
    "    for char in text:\n",
    "        i = 0\n",
    "        for item in char_frequency:\n",
    "            if char == item[0]:\n",
    "                ret += codes[i]\n",
    "            i += 1\n",
    "\n",
    "    return ret\n",
    "\n",
    "\n",
    "# 解码整个字符串\n",
    "def decode_str(huffman_str, char_frequency, codes):\n",
    "    ret = ''\n",
    "    while huffman_str != '':\n",
    "        i = 0\n",
    "        for item in codes:\n",
    "            if item in huffman_str and huffman_str.index(item) == 0:\n",
    "                ret += char_frequency[i][0]\n",
    "                huffman_str = huffman_str[len(item):]\n",
    "            i += 1\n",
    "\n",
    "    return ret\n",
    "\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    text = '1211123'\n",
    "\n",
    "    char_frequency = count_frequency(text)\n",
    "    char_frequency = [('12',2),('3',1),('122',4)]\n",
    "    nodes = create_nodes([item[1] for item in char_frequency])\n",
    "    root = create_huffman_tree(nodes)\n",
    "    codes = huffman_encoding(nodes, root)\n",
    "\n",
    "    huffman_str = encode_str(text, char_frequency, codes)\n",
    "    origin_str = decode_str(huffman_str, char_frequency, codes)\n",
    "\n",
    "    print ('Encode result:' + huffman_str)\n",
    "    print ('Decode result:' + origin_str)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[<__main__.Node at 0x7f1a9c767fd0>,\n",
       " <__main__.Node at 0x7f1a9c7762e8>,\n",
       " <__main__.Node at 0x7f1a9c776358>]"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "nodes"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[('12', 2), ('3', 1), ('122', 4)]"
      ]
     },
     "execution_count": 31,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "char_frequency"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "['01', '00', '1']"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "codes"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
