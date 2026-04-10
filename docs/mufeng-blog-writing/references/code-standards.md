# Code Standards

## General Rules
- Provide runnable code blocks with context and imports.
- Add Chinese comments for key logic and pitfalls.
- Avoid isolated snippets without explanation.
- Include best practices and common pitfalls near the code when useful.

## Swift / iOS Example
```swift
// MARK: - ViewModel

/// 用户信息 ViewModel
class UserViewModel: ObservableObject {
    // MARK: Properties

    /// 用户名称
    @Published var username: String = ""

    /// 是否正在加载
    @Published var isLoading: Bool = false

    // MARK: Methods

    /// 获取用户信息
    /// - Parameter userId: 用户 ID
    /// - Returns: 用户数据或错误
    func fetchUserInfo(userId: String) async throws -> User {
        isLoading = true
        defer { isLoading = false }

        // 调用服务获取用户数据
        let user = try await userService.getUser(id: userId)
        return user
    }
}

// ✅ 最佳实践:
// 1. 使用 async/await 处理异步操作
// 2. 使用 @Published 管理 UI 状态
// 3. 使用 defer 确保状态复位

// ⚠️ 常见陷阱:
// 1. 忘记在 defer 中重置 loading 状态
// 2. 没有正确处理错误情况
```

## Java / Spring Boot Example
```java
/**
 * 用户服务实现
 *
 * @author Joey
 */
@Service
@Slf4j
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    /**
     * 根据 ID 获取用户信息
     *
     * @param userId 用户 ID
     * @return 用户信息
     */
    @Override
    @Transactional(readOnly = true)
    public UserDTO getUserById(Long userId) {
        log.info("查询用户信息, userId: {}", userId);

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("用户不存在: " + userId));

        return UserMapper.toDTO(user);
    }
}

// ✅ 最佳实践:
// 1. 只读查询使用 @Transactional(readOnly = true)
// 2. 使用 DTO 返回，避免暴露 Entity
// 3. 记录关键日志用于排查

// ⚠️ 常见陷阱:
// 1. 直接返回 Entity 导致字段泄露
// 2. 忘记事务或错误处理
```

## Vue.js Example
```vue
<template>
  <div class="user-profile">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="user" class="user-info">
      <h2>{{ user.username }}</h2>
      <p>{{ user.email }}</p>
    </div>
    <div v-else class="error">加载失败</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { User } from '@/types'

const loading = ref(false)
const user = ref<User | null>(null)
const error = ref<Error | null>(null)

/**
 * 获取用户信息
 */
const fetchUser = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/user')
    user.value = await response.json()
  } catch (e) {
    error.value = e as Error
    console.error('获取用户信息失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUser()
})
</script>

<style scoped>
.user-profile {
  padding: 20px;
}
</style>

<!-- ✅ 最佳实践: -->
<!-- 1. 使用 Composition API + TypeScript -->
<!-- 2. 处理加载/成功/失败三种状态 -->
```

## TypeScript Example
```typescript
/**
 * 用户接口定义
 */
interface User {
  /** 用户 ID */
  id: string
  /** 用户名 */
  username: string
  /** 邮箱地址 */
  email: string
  /** 创建时间 */
  createdAt: Date
}

/**
 * API 响应包装
 */
interface ApiResponse<T> {
  /** 响应数据 */
  data: T
  /** 响应消息 */
  message: string
  /** 状态码 */
  code: number
}

/**
 * 用户服务类
 */
class UserService {
  /**
   * 获取用户信息
   * @param userId 用户 ID
   */
  async getUser(userId: string): Promise<User> {
    const response = await fetch(`/api/users/${userId}`)
    const result: ApiResponse<User> = await response.json()
    return result.data
  }
}

// ✅ 最佳实践:
// 1. 为 public API 添加 JSDoc
// 2. 使用泛型提高复用性
// 3. 避免 any
```
