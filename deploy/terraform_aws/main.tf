# main.tf
provider "aws" {
  region = "eu-west-3"
}

resource "aws_instance" "python_backend" {
  ami           = "ami-0c94855ba95c574c8" # This is an Amazon Linux 2 LTS AMI. Please replace with the correct AMI id if you're using a different region
  instance_type = "t2.micro"

  tags = {
    Name = "PythonBackend"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              service docker start
              usermod -a -G docker ec2-user
              docker pull {your_docker_image}
              docker run -d -p 5000:5000 {your_docker_image}
              EOF
}
