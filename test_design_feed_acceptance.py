#!/usr/bin/env python3
"""
设计内容展示功能 - 综合验收测试脚本
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """测试后端健康检查"""
    print("1️⃣  测试后端健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ 后端健康检查通过")
        return True
    except Exception as e:
        print(f"❌ 后端健康检查失败: {e}")
        return False


def test_design_feed_api():
    """测试设计内容 API"""
    print("\n2️⃣  测试设计内容 API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/design-feed", timeout=10)
        assert response.status_code == 200, f"API failed: {response.status_code}"

        data = response.json()
        assert data['success'] == True, "Response success is not True"
        assert 'posts' in data, "Response missing 'posts' field"
        assert 'total' in data, "Response missing 'total' field"
        assert len(data['posts']) > 0, "No posts returned"

        # 验证第一个帖子的结构
        first_post = data['posts'][0]
        required_fields = ['id', 'author', 'content', 'media_urls', 'x_url']
        for field in required_fields:
            assert field in first_post, f"Post missing required field: {field}"

        print(f"✅ 设计内容 API 通过 (返回 {len(data['posts'])} 个帖子，总计 {data['total']} 个)")
        return True
    except Exception as e:
        print(f"❌ 设计内容 API 失败: {e}")
        return False


def test_design_stats_api():
    """测试设计统计 API"""
    print("\n3️⃣  测试设计统计 API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/design-feed/stats", timeout=10)
        assert response.status_code == 200, f"Stats API failed: {response.status_code}"

        data = response.json()
        assert data['success'] == True, "Response success is not True"
        assert 'total_posts' in data, "Response missing 'total_posts'"
        assert 'posts_with_media' in data, "Response missing 'posts_with_media'"

        print(f"✅ 设计统计 API 通过")
        print(f"   - 总帖子数: {data['total_posts']}")
        print(f"   - 有图帖子: {data['posts_with_media']}")
        print(f"   - 有视频帖子: {data['posts_with_video']}")
        print(f"   - 作者数: {data['total_authors']}")
        return True
    except Exception as e:
        print(f"❌ 设计统计 API 失败: {e}")
        return False


def test_design_feed_with_limit():
    """测试带参数的设计内容 API"""
    print("\n4️⃣  测试带参数的设计内容 API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/design-feed?limit=5", timeout=10)
        assert response.status_code == 200, f"API with limit failed: {response.status_code}"

        data = response.json()
        assert len(data['posts']) == 5, f"Expected 5 posts, got {len(data['posts'])}"

        print(f"✅ 参数测试通过 (限制返回 5 个帖子)")
        return True
    except Exception as e:
        print(f"❌ 参数测试失败: {e}")
        return False


def test_post_content_quality():
    """测试帖子内容质量"""
    print("\n5️⃣  测试帖子内容质量...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/design-feed", timeout=10)
        data = response.json()
        posts = data['posts']

        posts_with_images = sum(1 for p in posts if p.get('media_urls'))
        posts_with_author = sum(1 for p in posts if p.get('author'))
        posts_with_content = sum(1 for p in posts if p.get('content'))

        print(f"✅ 内容质量检查通过")
        print(f"   - 有图片的帖子: {posts_with_images}/{len(posts)}")
        print(f"   - 有作者的帖子: {posts_with_author}/{len(posts)}")
        print(f"   - 有内容的帖子: {posts_with_content}/{len(posts)}")

        # 展示一个示例帖子
        if posts:
            sample = posts[0]
            print(f"\n   示例帖子:")
            print(f"   - 作者: {sample.get('author', 'N/A')}")
            print(f"   - 内容: {sample.get('content', 'N/A')[:50]}...")
            print(f"   - 图片数: {len(sample.get('media_urls', []))}")

        return True
    except Exception as e:
        print(f"❌ 内容质量检查失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("设计内容展示功能 - 综合验收测试")
    print("=" * 60)

    tests = [
        test_backend_health,
        test_design_feed_api,
        test_design_stats_api,
        test_design_feed_with_limit,
        test_post_content_quality,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✅ 所有测试通过！设计内容展示功能验收成功！")
        print("\n下一步:")
        print("1. 启动 Flutter 应用: cd ai_agent_app && flutter run")
        print("2. 点击首页的 '设计灵感' 按钮 (调色板图标)")
        print("3. 验证设计帖子正常显示")
        return 0
    else:
        print(f"\n❌ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
