# 🚀 Hướng Dẫn Build — Antigravity Tools

> Dự án **Antigravity Tools** là một ứng dụng desktop đa nền tảng xây dựng bằng **Tauri v2** (Rust backend) + **React 19 + TypeScript** (frontend), đóng gói bằng Vite.

---

## 📋 Yêu Cầu Hệ Thống

### Node.js & pnpm

| Công cụ | Phiên bản tối thiểu |
|---------|---------------------|
| Node.js | ≥ 18.x (khuyến nghị 20.x+) |
| pnpm    | ≥ 9.x |

Cài pnpm (nếu chưa có):

```bash
npm install -g pnpm
# hoặc
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

Kiểm tra:

```bash
pnpm --version
```

### Rust & Cargo

Tauri yêu cầu Rust toolchain. Cài đặt qua [rustup](https://rustup.rs/):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Sau khi cài xong, khởi động lại terminal hoặc chạy:

```bash
source $HOME/.cargo/env
```

Kiểm tra:

```bash
rustc --version   # rustc 1.78+
cargo --version
```

### macOS — Xcode Command Line Tools & CMake

```bash
xcode-select --install
brew install cmake
```

### Linux (Debian/Ubuntu) — System Dependencies

```bash
sudo apt update
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libgtk-3-dev \
  cmake
```

### Windows — Prerequisites

- [Microsoft Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/) (thường đã có sẵn trên Windows 10/11)

---

## ⚙️ Cài Đặt Tauri CLI

```bash
# Cài Tauri CLI v2 qua Cargo (global)
cargo install tauri-cli --version "^2"

# Hoặc dùng pnpm exec (đã có trong devDependencies)
pnpm exec tauri --version
```

---

## 📦 Cài Đặt Node Packages

```bash
pnpm install
```

Sau khi install xong, chạy lệnh sau để approve build scripts cho các native package (`esbuild`, `@tauri-apps/cli`):

```bash
pnpm approve-builds
```

Khi có prompt, nhấn `a` để chọn tất cả rồi Enter, tiếp tục nhấn `y` để xác nhận. Lệnh này có thể cần chạy **2 lần** (một lần cho `esbuild`, một lần cho `@tauri-apps/cli`).

> **Lưu ý:** pnpm tự động xử lý peer dependency linh hoạt hơn npm. Nếu vẫn gặp lỗi peer deps, thêm vào `package.json`:
>
> ```json
> "pnpm": {
>   "overrides": {
>     "antd": "^5.24.6"
>   }
> }
> ```

---

## 🛠️ Chạy Development

### Frontend only (Vite dev server)

```bash
pnpm dev
```

Truy cập tại: `http://localhost:1420`

### Tauri dev (Desktop App)

```bash
pnpm tauri dev
```

Hoặc với Rust log debug:

```bash
pnpm tauri:debug
```

> Lần đầu chạy sẽ tốn thời gian compile Rust (~5–15 phút tùy máy). Các lần sau sẽ nhanh hơn nhờ incremental compilation.

---

## 📦 Build Production

### Build Frontend (Vite)

```bash
pnpm build
```

Output sẽ ở thư mục `./dist/`.

### Build Tauri App (Desktop binary)

Chạy lệnh build tiêu chuẩn (mặc định build theo kiến trúc của thiết bị hiện tại):

```bash
pnpm tauri build
```

Nếu muốn build cụ thể cho macOS chip Apple Silicon (M1/M2/M3...), hãy chỉ định target:

```bash
pnpm tauri build --target aarch64-apple-darwin
```

#### Vị trí file đầu ra (Output DMG):

Sau khi quá trình build thành công, file cài đặt `.dmg` sẽ nằm trong các thư mục sau:

- **macOS Apple Silicon (M1/M2/M3):**
  - Thư mục: `src-tauri/target/aarch64-apple-darwin/release/bundle/dmg/`
  - Tên file: `Antigravity Tools_<version>_aarch64.dmg`
- **macOS Intel:**
  - Thư mục: `src-tauri/target/x86_64-apple-darwin/release/bundle/dmg/` (hoặc `src-tauri/target/release/bundle/dmg/`)
- **Windows:**
  - Thư mục: `src-tauri/target/release/bundle/nsis/` hoặc `msi/`
- **Linux:**
  - Thư mục: `src-tauri/target/release/bundle/deb/` hoặc `appimage/`

> **Lưu ý macOS:** Dự án đã được cấu hình tắt tính năng tạo chữ ký cập nhật (`createUpdaterArtifacts: false` trong `tauri.conf.json`) khi build local, giúp bạn đóng gói thành công file `.dmg` mà không cần thiết lập biến môi trường `TAURI_SIGNING_PRIVATE_KEY`.

---

## 🐳 Docker (tùy chọn)

Nếu có cấu hình Docker trong thư mục `./docker/`:

```bash
docker build -f docker/Dockerfile -t antigravity-tools .
docker run --rm antigravity-tools
```

---

## 🔧 Scripts Hữu Ích

| Lệnh | Mô tả |
|------|-------|
| `pnpm dev` | Khởi động Vite dev server (frontend) |
| `pnpm build` | Build frontend production |
| `pnpm preview` | Preview bản build production |
| `pnpm tauri dev` | Chạy Tauri app ở chế độ development |
| `pnpm tauri build` | Build Tauri app production |
| `pnpm tauri:debug` | Chạy Tauri với RUST_LOG=debug |

---

## 🗂️ Cấu Trúc Dự Án

```
Antigravity-Manager/
├── src/                    # Frontend React + TypeScript
├── src-tauri/              # Rust backend (Tauri)
│   ├── src/
│   │   ├── main.rs
│   │   ├── lib.rs
│   │   ├── commands/       # Tauri commands
│   │   ├── models/
│   │   ├── modules/
│   │   ├── proxy/          # Reverse proxy service
│   │   └── utils/
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri configuration
├── dist/                   # Frontend build output
├── public/                 # Static assets
├── package.json            # Node dependencies & scripts
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

---

## 🔑 Các Dependency Chính

### Frontend

| Package | Phiên bản | Mô tả |
|---------|-----------|-------|
| React | ^19.1.0 | UI framework |
| Ant Design | ^5.24.6 | UI component library |
| Tauri API | ^2 | Desktop API bindings |
| React Router | ^7.12.0 | Client-side routing |
| Zustand | ^5.0.9 | State management |
| Framer Motion | ^11.13.1 | Animations |
| i18next | ^25.7.2 | Internationalization |
| Recharts | ^3.5.1 | Charts |
| @lobehub/ui | ^4.33.4 | Lobe Hub UI components |

### Rust (Tauri Backend)

| Crate | Mô tả |
|-------|-------|
| tauri ^2.2.5 | Desktop framework |
| axum 0.7 | HTTP server (reverse proxy) |
| reqwest 0.12 | HTTP client |
| rusqlite 0.32 | SQLite embedded database |
| tokio 1 | Async runtime |
| serde / serde_json | Serialization |
| tracing | Logging |

---

## ❗ Troubleshooting

### Lỗi peer dependency khi `pnpm install`

Thêm cấu hình `pnpm.overrides` vào `package.json`:

```json
{
  "pnpm": {
    "overrides": {
      "antd": "^5.24.6"
    }
  }
}
```

---

### Lỗi `rustc: command not found`

Rust chưa được cài hoặc chưa thêm vào PATH:

```bash
# Cài Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Thêm vào PATH (tạm thời)
source $HOME/.cargo/env

# Hoặc thêm vào ~/.zshrc / ~/.bashrc
echo 'source $HOME/.cargo/env' >> ~/.zshrc
```

---

### Lỗi link error trên Linux

```bash
sudo apt install -y libssl-dev pkg-config
```

---

### Lỗi build trên macOS — `xcrun: error`

```bash
xcode-select --install
sudo xcode-select --reset
```

---

### Cổng 1420 bị chiếm

Chỉnh `devUrl` trong `src-tauri/tauri.conf.json` và `server.port` trong `vite.config.ts`:

```json
// tauri.conf.json
"devUrl": "http://localhost:1421"
```

```ts
// vite.config.ts
server: { port: 1421 }
```

---

## 📚 Tài Liệu Tham Khảo

- [Tauri v2 Documentation](https://v2.tauri.app/)
- [Tauri v2 Prerequisites](https://v2.tauri.app/start/prerequisites/)
- [pnpm Documentation](https://pnpm.io/)
- [Vite Documentation](https://vitejs.dev/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [Ant Design v5](https://ant.design/)
