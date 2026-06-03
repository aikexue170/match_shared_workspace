#!/usr/bin/env python3
import serial
import time
import threading
from yis_std_dec import std_decoder   # 官方解码器模块

class IMU:
    def __init__(self, port, baudrate=460800, timeout=0.01):
        """
        初始化 IMU 类
        :param port: 串口设备名，例如 '/dev/ttyACM0' 或 'COM9'
        :param baudrate: 波特率，默认 460800
        :param timeout: 串口读取超时（秒）
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.decoder = std_decoder()
        self.buffer = bytearray()
        self._data = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def open(self):
        """打开串口并启动后台读取线程"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        print(f"IMU 串口已打开: {self.ser.name}")
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def close(self):
        """关闭串口和后台线程"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("IMU 串口已关闭")

    def _read_loop(self):
        """后台线程：持续读取串口数据并解析"""
        while self._running:
            if self.ser.in_waiting:
                chunk = self.ser.read(self.ser.in_waiting)
                self.buffer.extend(chunk)

                # 循环解析所有完整帧
                while True:
                    sensor_data = {}
                    ret = self.decoder.proc_data(self.buffer, len(self.buffer), sensor_data, dbg_flg=False)
                    if not ret:
                        break
                    # 解析成功，更新内部数据字典
                    with self._lock:
                        # 将新解析的数据合并到 _data 中
                        self._data.update(sensor_data)
            else:
                time.sleep(0.0005)   # 避免空转

    def get_data(self):
        """返回最新一帧数据的副本（字典）"""
        with self._lock:
            return self._data.copy()

    def get_value(self, key, default=None):
        """获取指定键的值，若不存在则返回 default"""
        with self._lock:
            return self._data.get(key, default)

    def is_running(self):
        return self._running

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
