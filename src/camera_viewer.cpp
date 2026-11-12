#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <opencv2/imgproc/imgproc.hpp>
// highgui 헤더 삭제 (화면 출력 안함)

/**
 * @class CameraViewer
 * @brief 화면 출력 없이 토픽만 2개 발행하는 노드
 * 1. 구독: /camera/image_raw
 * 2. 발행1: /camera/image_original_relay (원본 재전송)
 * 3. 발행2: /camera/image_corrected (180도 회전)
 */
class CameraViewer : public rclcpp::Node
{
public:
  CameraViewer() : Node("camera_viewer_node")
  {
    // 1. 구독자 (Subscriber) 설정
    // QoS 10 설정
    sub_ = this->create_subscription<sensor_msgs::msg::Image>(
      "/camera/image_raw", 10,
      std::bind(&CameraViewer::imageCallback, this, std::placeholders::_1));

    
    // 3. 발행자 2 (Publisher) - 180도 보정 영상
    pub_corrected_ = this->create_publisher<sensor_msgs::msg::Image>(
      "/camera/image_corrected", 10);

    RCLCPP_INFO(this->get_logger(), "Camera Viewer Node Started (Topic Only Mode).");
  }

private:
  void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    // [Step 1] ROS 메시지 -> OpenCV 변환
    cv_bridge::CvImagePtr cv_ptr;
    try {
      cv_ptr = cv_bridge::toCvCopy(msg, msg->encoding);
    } catch (cv_bridge::Exception& e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }


    // [Step 3] 180도 회전 처리
    cv::Mat flipped_image;
    // flipCode -1: 상하좌우 반전 (180도 회전)
    cv::flip(cv_ptr->image, flipped_image, -1);

    // [Step 4] 보정된 토픽 발행 (화면 출력 X)
    sensor_msgs::msg::Image::SharedPtr flipped_msg = 
      cv_bridge::CvImage(msg->header, msg->encoding, flipped_image).toImageMsg();
    
    pub_corrected_->publish(*flipped_msg);
  }

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_corrected_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CameraViewer>());
  rclcpp::shutdown();
  return 0;
}