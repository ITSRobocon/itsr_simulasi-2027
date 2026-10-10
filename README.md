# robocon_2027_sim

Simulasi robot mecanum (TR) untuk Robocon 2027, pakai ROS 2 Humble + Webots R2025a,
dengan visualisasi RViz yang mengikuti posisi robot secara real-time.

## Prasyarat (install di level sistem, bukan lewat pip)

Dua hal ini **wajib** diinstall dulu sebelum langkah apapun di bawah. Semua
import di source code (`rclpy`, `geometry_msgs`, `webots_ros2_driver`, dst)
berasal dari ROS 2 / Webots, bukan dari PyPI, jadi tidak ada `pip install`
yang menggantikan langkah ini:

1. **ROS 2 Humble** (Ubuntu 22.04)
   https://docs.ros.org/en/humble/Installation.html
2. **Webots R2025a**
   https://cyberbotics.com/doc/guide/installation-procedure

## 1. Clone repo

```bash
mkdir -p simulasi-2027_ws/src
cd simulasi-2027_ws/src
git clone https://github.com/ITSRobocon/itsr_simulasi-2027.git
```

## 2. (Opsional) Buat virtual environment Python

Project ini saat ini **tidak punya dependency pip pihak ketiga**, jadi
langkah ini **boleh dilewati sepenuhnya** untuk menjalankan simulasi
Webots + ROS 2. Simpan langkah ini kalau nanti kamu menambahkan
script/tooling Python yang butuh library luar (mis. numpy, openCV) -
baru saat itu buat `requirements.txt` dan install di venv ini.

Pastikan dulu versi Python-nya 3.10.x (bawaan ROS 2 Humble di Ubuntu 22.04):

```bash
python3 --version
```

```bash
python -m venv .venv
source .venv/bin/activate        

pip install -r requirements.txt  # hanya kalau file ini sudah ada/diisi
```

> **Catatan penting:** venv Python yang dibuat dengan `python -m venv` itu
> terisolasi dari package sistem secara default, termasuk `rclpy` dan
> paket ROS 2 lain yang letaknya di `/opt/ros/humble/...`. Kalau kamu
> aktifkan venv ini lalu coba `ros2 launch ...` di dalamnya, kemungkinan
> besar akan error `ModuleNotFoundError: rclpy`. Kalau memang butuh venv
> aktif bersamaan dengan ROS 2, buat dengan flag tambahan:
> ```bash
> python -m venv .venv --system-site-packages
> ```
> supaya venv tetap bisa melihat package ROS 2 yang sudah diinstall di sistem.

## 3. Install dependency ROS 2 (rosdep)

Ini yang jadi "requirements.txt" sesungguhnya untuk workspace ROS 2 - dia
baca tiap `package.xml` di `src/` dan install paket apt yang dibutuhkan
(`ros-humble-rclpy`, `ros-humble-webots-ros2-driver`, `ros-humble-rviz2`, dst).

```bash
sudo apt install python3-rosdep
sudo rosdep init    # lewati kalau sudah pernah dijalankan sebelumnya
rosdep update

# dari root workspace (folder yang berisi folder src/)
cd ..
rosdep install --from-paths src --ignore-src -r -y
```

## 4. Build workspace

```bash
colcon build
source install/setup.bash
```

## 5. Jalankan simulasi + RViz

```bash
ros2 launch ./src/itsr_simulasi-2027/launch/bringup.launch.py
```

Ini akan membuka Webots (dunia `simple_arena.wbt`) dan RViz sekaligus; posisi
dan putaran roda robot di RViz mengikuti kondisi aktual robot di Webots.

## 6. Kirim perintah gerak

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```
