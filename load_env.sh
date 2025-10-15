#!/usr/bin/env bash
set -euo pipefail

ROS_DISTRO=humble
WS=~/ros2_gz_ws

echo "[1/8] 安装基础依赖..."
sudo apt-get update
sudo apt-get install -y python3-vcstool python3-colcon-common-extensions \
    build-essential cmake git

echo "[2/8] 创建工作区..."
mkdir -p "$WS/src"
cd "$WS"

echo "[3/8] 拉取 gazebo_ros_pkgs（Humble 分支），并切到 3.8.x 稳定点对齐 Gazebo 11.10.2..."
# 官方仓库
if [ ! -d src/gazebo_ros_pkgs ]; then
  git clone https://github.com/ros-simulation/gazebo_ros_pkgs.git src/gazebo_ros_pkgs
fi
cd src/gazebo_ros_pkgs
git fetch --all --tags
# 3.8 系列（与 2024 年 Ubuntu Gazebo 11.10.x 更贴近）；如需要可改成具体 tag：gazebo_ros_pkgs-3.8.0
git checkout humble
git checkout gazebo_ros_pkgs-3.8.0
cd "$WS"

echo "[4/8] 安装依赖（基于当前系统 Gazebo 11.10.2）..."
sudo rosdep init 2>/dev/null || true
rosdep update
rosdep install --from-paths src --ignore-src -y --rosdistro $ROS_DISTRO

echo "[5/8] 构建（关闭测试以加快&减少依赖）..."
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --merge-install \
  --cmake-args -DBUILD_TESTING=OFF

echo "[6/8] 覆盖环境（优先使用你编译出的 3.8.x 插件库）..."
echo "source $WS/install/setup.bash" >> ~/.bashrc
source "$WS/install/setup.bash"

echo "[7/8] 校验插件实际解析路径..."
echo "查看 eol GUI 插件指向："
ldd $WS/install/lib/libgazebo_ros_eol_gui.so | egrep 'gazebo|Qt|Ogre' || true

echo "[8/8] 试跑（若有 GUI 问题，先无 GUI 验证）："
echo "  ros2 launch <pkg> <launch>.py gui:=false"
echo "完成。现在 gazebo_ros_pkgs 已固定到 3.8.x，与 gazebo 11.10.2 更匹配。"
