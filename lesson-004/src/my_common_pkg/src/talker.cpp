#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class Talker  : public rclcpp::Node
{
  public:
    Talker() : Node("talker")
    {
      // 创建publisher, 话题名"chatter", 队列大小
      publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);

      // 每500ms，调用一次这个发布的命令
      timer_ = this->create_wall_timer(500ms, std::bind(&Talker::timer_callback, this));
    }

  private:
    int count_ = 0;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;

    void timer_callback()
    {
      auto message = std_msgs::msg::String();
      message.data = "hello world " + std::to_string(count_++);
      RCLCPP_INFO(this->get_logger(), "Publishing: %s", message.data.c_str());
      // RCLCPP_WARN()
      // RCLCPP_ERROR()
      // RCLCPP_DEBUG()
      publisher_->publish(message);
    }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Talker>());
  rclcpp::shutdown();
  return 0;
}
