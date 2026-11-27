import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

with Robot(ROBOT_IP) as robot:
    try:
        ok(robot.encoder.reset())
        ok(robot.pose.set(0, 0, 0))
        time.sleep(0.5)

        print("set:", ok(robot.go2point.set(1000, 0)))

        while True:
            st = ok(robot.go2point.status())
            if not st.get("active", False):
                break
            print(f"fase={st.get('phase')}  err=({st.get('x_error', 0):.0f}, {st.get('y_error', 0):.0f}) mm")
            time.sleep(0.1)

        print("status final:", st)
        print("pose final:  ", ok(robot.pose.get()))
        print("encoder:     ", ok(robot.encoder.read()))
    finally:
        try:
            robot.go2point.stop()
        except Exception:
            pass