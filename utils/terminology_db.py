import json
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer


class TerminologyDatabase:
    """基于向量的术语数据库，用于保持翻译一致性"""

    def __init__(self, data_path: str = "data/terminology.json"):
        """初始化术语数据库

        Args:
            data_path: 术语JSON文件路径
        """
        self.data_path = data_path
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        self.knn = None
        self.terms = []
        self.translations = []
        self.embeddings = None

        # 如果文件存在，加载术语
        if os.path.exists(data_path):
            self.load_terminology()
        else:
            # 初始化为空数据库并创建文件
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            self.save_terminology()

    def load_terminology(self) -> None:
        """从文件加载术语"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 重置数据结构
            self.terms = []
            self.translations = []

            # 加载术语
            for item in data:
                self.terms.append(item["term"])
                self.translations.append(item["translation"])

            # 创建向量和KNN索引
            if self.terms:
                self.embeddings = self.vectorizer.fit_transform(self.terms)
                self.knn = NearestNeighbors(n_neighbors=min(5, len(self.terms)), metric="cosine")
                self.knn.fit(self.embeddings)

        except Exception as e:
            print(f"加载术语时出错：{str(e)}")
            # 初始化为空
            self.terms = []
            self.translations = []
            self.embeddings = None
            self.knn = None

    def save_terminology(self) -> None:
        """保存术语到文件"""
        data = [
            {"term": term, "translation": translation}
            for term, translation in zip(self.terms, self.translations)
        ]

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_term(self, term: str, translation: str) -> None:
        """添加术语到术语数据库

        Args:
            term: 源术语
            translation: 术语的翻译
        """
        # 检查术语是否已存在
        if term in self.terms:
            idx = self.terms.index(term)
            self.translations[idx] = translation
        else:
            # 添加新术语
            self.terms.append(term)
            self.translations.append(translation)

            # 重新创建向量和KNN索引
            self.embeddings = self.vectorizer.fit_transform(self.terms)
            self.knn = NearestNeighbors(n_neighbors=min(5, len(self.terms)), metric="cosine")
            self.knn.fit(self.embeddings)

        # 保存更新
        self.save_terminology()

    def search(self, text: str, threshold: float = 0.3, max_results: int = 5) -> List[Dict[str, str]]:
        """在文本中搜索匹配的术语

        Args:
            text: 要搜索术语的文本
            threshold: 相似度阈值 (0-1)，越小越严格
            max_results: 返回的最大结果数量

        Returns:
            匹配的术语和翻译列表
        """
        if not self.terms or self.knn is None:
            return []

        # 编码文本
        text_vector = self.vectorizer.transform([text])

        # 搜索
        distances, indices = self.knn.kneighbors(text_vector, n_neighbors=min(max_results, len(self.terms)))

        # 按阈值过滤并返回结果
        results = []

        for i, idx in enumerate(indices[0]):
            # 余弦距离转换为相似度 (1 - 距离)
            similarity = 1 - distances[0][i]
            if similarity > threshold:
                results.append({
                    "term": self.terms[idx],
                    "translation": self.translations[idx]
                })

        return results

    def batch_search(self, text: str, threshold: float = 0.3) -> List[Dict[str, str]]:
        """搜索可能出现在文本中的所有术语

        Args:
            text: 要搜索的文本
            threshold: 相似度阈值 (0-1)

        Returns:
            潜在术语匹配列表
        """
        # 对于较长的文本，拆分为句子并搜索每个句子
        # 用于演示目的的简单句子拆分
        sentences = text.split(". ")

        all_results = []
        for sentence in sentences:
            matches = self.search(sentence, threshold)
            all_results.extend(matches)

        # 去除重复结果
        unique_results = []
        seen_terms = set()

        for result in all_results:
            if result["term"] not in seen_terms:
                seen_terms.add(result["term"])
                unique_results.append(result)

        return unique_results
