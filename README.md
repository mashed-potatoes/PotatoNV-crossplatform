# Install
- pip3 install -r requirements.txt

# Instructions
After the device is in test mode ( see https://github.com/mashed-potatoes/PotatoNV/issues/20 ):
Using dmesg -w, you can verify that the device is in test mode 
![image info](./images/testmode.png)

# Commands in test mode

- cd usrlock && python3 main.py

# Requirements 
This program works with python-3.9

Tested in Manjaro linux v5.10.23-1-MANJARO

# License
All bootloaders are Huawei Technologies Co., Ltd. property.

Usrlock - CLI utility for unlocking Huawei devices on Kirin SoCs.
Copyright (C) 2019  Penn Mackintosh (penn5)
Copyright (C) 2020  Andrey Smirnoff (mashed-potatoes)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
