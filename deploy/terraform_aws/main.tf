# main.tf
provider "aws" {
  region = "eu-west-3"
}

resource "aws_instance" "python_backend" {
  ami           = "ami-0f61de2873e29e866"
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
              docker run -d -p 8081:8081 {your_docker_image}
              EOF
}
