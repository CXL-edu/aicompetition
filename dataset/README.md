# 数据集

将dataset压缩包解压至该文件夹

得到的目录结构为：
```markdown
dataset
 ┣ README.md
 ┣ demo_item.json
 ┣ demo_review.json
 ┣ demo_user.json
 ┣ item.json
 ┣ review.json
 ┗ user.json
```


<br><br><br>
***
# 数据分析
***


# 🌟User数据统计
`user.json`文件数据分析，其中仅yelp数据集中的user数据包含大量有效信息，amazon和goodreads数据集中的user数据仅包含user_id和source信息

分析结果:
- yelp的user数据中，friends字段包含太多user_id，而且难以从中提取有效信息，应当删除
- yelp的user数据中，elite字段缺失太多，仅存36875/558111=6.6%,其可能表示用户活跃的年份，参考价值可能不大，删除

## yelp:
| Field              |   Count | Percentage of Missing   | 待补充的分析   |
|:-------------------|:-------:|:-----------------------:|:---------------:|
| user_id            |  558111 | 0.00%                   | 用户id |
| name               |  558111 | 0.00%                   | 用户名称 |
| review_count       |  558111 | 0.00%                   | 用户评论次数 |
| yelping_since      |  558111 | 0.00%                   | 用户注册时间 |
| useful             |  558111 | 0.00%                   | 用户评论被标记为useful的次数 |
| funny              |  558111 | 0.00%                   | 用户评论被标记为funny的次数 |
| cool               |  558111 | 0.00%                   | 用户评论被标记为cool的次数 |
| elite              |   36875 | 93.39%                  | `无效信息`，用户活跃年份 |
| friends            |  558111 | 0.00%                   | `冗余数据`，用户好友的user_id列表 |
| fans               |  558111 | 0.00%                   | 用户粉丝数量 |
| average_stars      |  558111 | 0.00%                   | 用户平均评分 |
| compliment_hot     |  558111 | 0.00%                   |                |
| compliment_more    |  558111 | 0.00%                   |                |
| compliment_profile |  558111 | 0.00%                   |                |
| compliment_cute    |  558111 | 0.00%                   |                |
| compliment_list    |  558111 | 0.00%                   |                |
| compliment_note    |  558111 | 0.00%                   |                |
| compliment_plain   |  558111 | 0.00%                   |                |
| compliment_cool    |  558111 | 0.00%                   |                |
| compliment_funny   |  558111 | 0.00%                   |                |
| compliment_writer  |  558111 | 0.00%                   |                |
| compliment_photos  |  558111 | 0.00%                   |                |
| source             |  558111 | 0.00%                   |                |

## amazon:
| Field   |   Count | Percentage of Missing   | 待补充的分析   |
|---------|---------|-------------------------|----------------|
| user_id |  194216 | 0.00%                   |                |
| source  |  194216 | 0.00%                   |                |

## goodreads:
| Field   |   Count | Percentage of Missing   | 待补充的分析   |
|---------|---------|-------------------------|----------------|
| user_id |  137371 | 0.00%                   |                |
| source  |  137371 | 0.00%                   |                |

---

# 🌟Item数据统计

## yelp:
| Field        |   Count | Percentage of Missing   | 待补充的分析   |
|--------------|---------|-------------------------|----------------|
| item_id      |   32869 | 0.00%                   |                |
| name         |   32869 | 0.00%                   |                |
| address      |   31568 | 3.96%                   |                |
| city         |   32869 | 0.00%                   |                |
| state        |   32869 | 0.00%                   |                |
| postal_code  |   32854 | 0.05%                   |                |
| latitude     |   32869 | 0.00%                   |                |
| longitude    |   32869 | 0.00%                   |                |
| stars        |   32869 | 0.00%                   |                |
| review_count |   32869 | 0.00%                   |                |
| is_open      |   32869 | 0.00%                   |                |
| attributes   |   32869 | 0.00%                   |                |
| categories   |   32869 | 0.00%                   |                |
| hours        |   32869 | 0.00%                   |                |
| source       |   32869 | 0.00%                   |                |
| type         |   32869 | 0.00%                   |                |

## amazon:
| Field           |   Count | Percentage of Missing   | 待补充的分析   |
|-----------------|---------|-------------------------|----------------|
| main_category   |   76047 | 0.00%                   |                |
| title           |   76042 | 0.01%                   |                |
| average_rating  |   76047 | 0.00%                   |                |
| rating_number   |   76047 | 0.00%                   |                |
| features        |   69415 | 8.72%                   |                |
| description     |   51301 | 32.54%                  |                |
| price           |   76047 | 0.00%                   |                |
| images          |   76039 | 0.01%                   |                |
| store           |   76047 | 0.00%                   |                |
| categories      |   73714 | 3.07%                   |                |
| details         |   75030 | 1.34%                   |                |
| item_id         |   76047 | 0.00%                   |                |
| bought_together |   76047 | 0.00%                   |                |
| subtitle        |   76047 | 0.00%                   |                |
| author          |   76047 | 0.00%                   |                |
| source          |   76047 | 0.00%                   |                |
| type            |   76047 | 0.00%                   |                |
| videos          |   44202 | 41.88%                  |                |

## goodreads:
| Field                |   Count | Percentage of Missing   | 待补充的分析   |
|----------------------|---------|-------------------------|----------------|
| isbn                 |  185717 | 25.72%                  |                |
| text_reviews_count   |  250007 | 0.00%                   |                |
| country_code         |  250007 | 0.00%                   |                |
| popular_shelves      |  250007 | 0.00%                   |                |
| is_ebook             |  250007 | 0.00%                   |                |
| average_rating       |  250007 | 0.00%                   |                |
| kindle_asin          |   81149 | 67.54%                  |                |
| description          |  211957 | 15.22%                  |                |
| format               |  200247 | 19.90%                  |                |
| link                 |  250007 | 0.00%                   |                |
| authors              |  250007 | 0.00%                   |                |
| publisher            |  204404 | 18.24%                  |                |
| num_pages            |  190499 | 23.80%                  |                |
| publication_day      |  160733 | 35.71%                  |                |
| isbn13               |  201882 | 19.25%                  |                |
| publication_month    |  175802 | 29.68%                  |                |
| publication_year     |  205865 | 17.66%                  |                |
| url                  |  250007 | 0.00%                   |                |
| image_url            |  250007 | 0.00%                   |                |
| item_id              |  250007 | 0.00%                   |                |
| ratings_count        |  250007 | 0.00%                   |                |
| work_id              |  250007 | 0.00%                   |                |
| title                |  250004 | 0.00%                   |                |
| title_without_series |  250004 | 0.00%                   |                |
| source               |  250007 | 0.00%                   |                |
| type                 |  250007 | 0.00%                   |                |
| series               |  105263 | 57.90%                  |                |
| similar_books        |  113810 | 54.48%                  |                |
| language_code        |  128435 | 48.63%                  |                |
| edition_information  |   16125 | 93.55%                  |                |
| asin                 |   20185 | 91.93%                  |                |

---

# 🌟Review数据统计


## yelp:
| Field        |   Count | Percentage of Missing   | 待补充的分析   |
|--------------|---------|-------------------------|----------------|
| item_id      |   32869 | 0.00%                   |                |
| name         |   32869 | 0.00%                   |                |
| address      |   31568 | 3.96%                   |                |
| city         |   32869 | 0.00%                   |                |
| state        |   32869 | 0.00%                   |                |
| postal_code  |   32854 | 0.05%                   |                |
| latitude     |   32869 | 0.00%                   |                |
| longitude    |   32869 | 0.00%                   |                |
| stars        |   32869 | 0.00%                   |                |
| review_count |   32869 | 0.00%                   |                |
| is_open      |   32869 | 0.00%                   |                |
| attributes   |   32869 | 0.00%                   |                |
| categories   |   32869 | 0.00%                   |                |
| hours        |   32869 | 0.00%                   |                |
| source       |   32869 | 0.00%                   |                |
| type         |   32869 | 0.00%                   |                |

## amazon:
| Field           |   Count | Percentage of Missing   | 待补充的分析   |
|-----------------|---------|-------------------------|----------------|
| main_category   |   76047 | 0.00%                   |                |
| title           |   76042 | 0.01%                   |                |
| average_rating  |   76047 | 0.00%                   |                |
| rating_number   |   76047 | 0.00%                   |                |
| features        |   69415 | 8.72%                   |                |
| description     |   51301 | 32.54%                  |                |
| price           |   76047 | 0.00%                   |                |
| images          |   76039 | 0.01%                   |                |
| store           |   76047 | 0.00%                   |                |
| categories      |   73714 | 3.07%                   |                |
| details         |   75030 | 1.34%                   |                |
| item_id         |   76047 | 0.00%                   |                |
| bought_together |   76047 | 0.00%                   |                |
| subtitle        |   76047 | 0.00%                   |                |
| author          |   76047 | 0.00%                   |                |
| source          |   76047 | 0.00%                   |                |
| type            |   76047 | 0.00%                   |                |
| videos          |   44202 | 41.88%                  |                |

## goodreads:
| Field                |   Count | Percentage of Missing   | 待补充的分析   |
|----------------------|---------|-------------------------|----------------|
| isbn                 |  185717 | 25.72%                  |                |
| text_reviews_count   |  250007 | 0.00%                   |                |
| country_code         |  250007 | 0.00%                   |                |
| popular_shelves      |  250007 | 0.00%                   |                |
| is_ebook             |  250007 | 0.00%                   |                |
| average_rating       |  250007 | 0.00%                   |                |
| kindle_asin          |   81149 | 67.54%                  |                |
| description          |  211957 | 15.22%                  |                |
| format               |  200247 | 19.90%                  |                |
| link                 |  250007 | 0.00%                   |                |
| authors              |  250007 | 0.00%                   |                |
| publisher            |  204404 | 18.24%                  |                |
| num_pages            |  190499 | 23.80%                  |                |
| publication_day      |  160733 | 35.71%                  |                |
| isbn13               |  201882 | 19.25%                  |                |
| publication_month    |  175802 | 29.68%                  |                |
| publication_year     |  205865 | 17.66%                  |                |
| url                  |  250007 | 0.00%                   |                |
| image_url            |  250007 | 0.00%                   |                |
| item_id              |  250007 | 0.00%                   |                |
| ratings_count        |  250007 | 0.00%                   |                |
| work_id              |  250007 | 0.00%                   |                |
| title                |  250004 | 0.00%                   |                |
| title_without_series |  250004 | 0.00%                   |                |
| source               |  250007 | 0.00%                   |                |
| type                 |  250007 | 0.00%                   |                |
| series               |  105263 | 57.90%                  |                |
| similar_books        |  113810 | 54.48%                  |                |
| language_code        |  128435 | 48.63%                  |                |
| edition_information  |   16125 | 93.55%                  |                |
| asin                 |   20185 | 91.93%                  |                |


# 其他 
浅浅添加一下Amazon；Yelp和Goodreads暂未找到官方数据表格，而找到的Amazon数据表格与上面的表格有些不同，故添加在下面：

## Amazon (https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)
### 用户评论（For User Reviews）

| 字段 (Field)       | 类型 (Type) | 说明 (Explanation)                                                                                                                                                    |
|--------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| rating             | float      | 产品评分（范围为 1.0 到 5.0）。                                                                                                                                       |
| title              | str        | 用户评论的标题。                                                                                                                                                       |
| text               | str        | 用户评论的正文内容。                                                                                                                                                   |
| images             | list       | 用户收到商品后发布的图片列表。每张图片有不同尺寸（small, medium, large），分别用 small_image_url、medium_image_url 和 large_image_url 表示。                            |
| asin               | str        | 产品的 ASIN（ID）。                                                                                                                                                   |
| parent_asin        | str        | 产品的父级 ASIN。**注意：**具有不同颜色、款式、尺寸的产品通常共享相同的父级 ASIN。在以往的亚马逊数据集中，“asin” 实际上就是父级 ASIN。请使用父级 ASIN 查找产品元信息。 |
| user_id            | str        | 评论者的用户 ID。                                                                                                                                                     |
| timestamp          | int        | 评论的时间（Unix 时间戳）。                                                                                                                                            |
| verified_purchase  | bool       | 是否为已验证购买。                                                                                                                                                     |
| helpful_vote       | int        | 该评论获得的“有帮助”票数。                                                                                                                                             |

---

### 产品元信息（For Item Metadata）

| 字段 (Field)       | 类型 (Type) | 说明 (Explanation)                                                                                                                             |
|--------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| main_category      | str        | 产品的主要类别（例如所在领域）。                                                                                                                    |
| title              | str        | 产品名称。                                                                                                                                      |
| average_rating     | float      | 产品页面上显示的平均评分。                                                                                                                       |
| rating_number      | int        | 产品的评分数量。                                                                                                                                |
| features           | list       | 产品特征，以要点（bullet-point）形式列出。                                                                                                       |
| description        | list       | 产品描述。                                                                                                                                      |
| price              | float      | 以美元计价的产品价格（爬取时的价格）。                                                                                                            |
| images             | list       | 产品图片列表。每张图片有不同尺寸（thumb, large, hi_res），其中 “variant” 字段表示图片所在位置或种类。                                               |
| videos             | list       | 产品相关视频，包括标题和链接（url）。                                                                                                            |
| store              | str        | 产品所属店铺名称。                                                                                                                               |
| categories         | list       | 产品的分层类别。                                                                                                                                |
| details            | dict       | 产品的详细信息，例如材料、品牌、尺寸等。                                                                                                         |
| parent_asin        | str        | 产品的父级 ASIN。                                                                                                                                |
| bought_together    | list       | 网站推荐的捆绑购买列表。                                                                                                                        |
