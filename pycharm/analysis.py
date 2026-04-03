import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from skopt import BayesSearchCV
import joblib
from skopt.space import Real
import re

# 尝试加载黑名单数据
try:
    # 读取CSV文件
    black_urls_df = pd.read_csv("C:\\Users\\41644\Desktop\所有url\黑全 - 副本.csv")
    # 提取'URL'列的内容，并将其转换为列表
    black_list = black_urls_df['URL'].tolist()
except Exception as e:
    print(f"Error reading the CSV file: {e}")
    exit(1)
# 加载测试文档数据

# 检查测试文档中的URL是否在黑名单中
# 加载训练数据
try:
    data = pd.read_csv("C:\\Users\\41644\Desktop\新建文件夹 (3)\黑库和白库.csv")
except Exception as e:
    print(f"Error reading the training data file: {e}")
    exit(1)
# 划分数据
X_train, X_test, y_train, y_test = train_test_split(data['url'], data['result'], test_size=0.2, random_state=None)

# 创建词袋模型
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 创建逻辑回归模型
model = LogisticRegression(max_iter=1000, solver='lbfgs')  # 明确指定solver

# 使用贝叶斯优化
search_spaces = {
    'C': (1e-6, 1e+6, 'log-uniform'),  # 仅保留l2支持的范围
    'penalty': ['l2']  # 移除l1选项
}
optimizer = BayesSearchCV(
    model,
    search_spaces,
    n_iter=32,
    cv=3,
    scoring='accuracy',
    random_state=42,
    n_jobs=-1
)
optimizer.fit(X_train_vec, y_train)

# 使用最优参数训练模型
best_model = LogisticRegression(max_iter=1000, **optimizer.best_params_)
best_model.fit(X_train_vec, y_train)

# 保存最佳模型和向量器
joblib.dump(best_model, 'best_model.joblib')
joblib.dump(vectorizer, 'vectorizer.joblib')

try:
    # 使用pandas读取CSV文件，并只获取'url'列
    test_urls_df = pd.read_csv("C:\\Users\\41644\Desktop\\test_results.csv", usecols=['url'])
    test_urls = test_urls_df['url'].tolist()
except Exception as e:
    print(f"Error reading the test file: {e}")
    exit(1)

# 注意：这里的 black_in_test 只是简单地检查测试URL是否在黑名单中，
# 它并不涉及模型预测。如果您想使用模型进行预测，请继续看下面的预测代码部分。
black_in_test = [url for url in test_urls if url in black_list]

# 注意：在实际预测之前，您不需要再次加载模型，因为这里只是示例。
# 但如果您在不同的脚本或会话中，您需要先加载模型：
best_model = joblib.load('best_model.joblib')
vectorizer = joblib.load('vectorizer.joblib')

# 对测试文档中的URL进行特征提取并预测（如果需要的话）
test_urls_vec = vectorizer.transform(test_urls)
test_pred = best_model.predict(test_urls_vec)


# 根据预测结果处理输出
predicted_black = [url for url, pred in zip(test_urls, test_pred) if pred == "black"]
predicted_black = list(set(predicted_black))  # 去重
predicted_black.extend(black_in_test)  # 将黑名单中的URL也加入列表
predicted_black = list(set(predicted_black))  # 再次去重
predicted_black_count = len(predicted_black)

# 根据列表是否有元素来输出结果
if predicted_black_count > 0:
    # 计算模型准确率（仅作为参考，因为测试集和实际应用的数据可能不同）
    y_pred_test = best_model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred_test)
    print(f"模型准确率: {accuracy:.4f}")

    print("black")
    for url in predicted_black:
        print(url)
else:
    print("white")