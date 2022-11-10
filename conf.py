import json
import glob

class PetConfig:
    """
    宠物配置
    """

    def __init__(self):
        self.petname = None
        self.width = 128
        self.height = 128
        self.refresh = 5
        self.interact_speed = 0.02
        self.dropspeed = 1.0
        self.gravity = 4.0
        self.default = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.drag = None
        self.fall = None
        self.random_act = []
        self.act_prob = []

    @classmethod
    def init_config(cls, pet_name: str, pic_dict: dict):
        # 初始化所有动作
        act_path = 'res/role/{}/act_conf.json'.format(pet_name)
        act_dict = {}
        with open(act_path, 'r', encoding='UTF-8') as f:
            act_dict = {k: Act.init_act(v, pic_dict, pet_name) for k, v in dict(json.load(f)).items()}
        path = 'res/role/{}/pet_conf.json'.format(pet_name)
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)
            # 初始化动作
            o.default = act_dict[conf_params['default']]
            o.up = act_dict[conf_params['up']]
            o.down = act_dict[conf_params['down']]
            o.left = act_dict[conf_params['left']]
            o.right = act_dict[conf_params['right']]
            o.drag = act_dict[conf_params['drag']]
            o.fall = act_dict[conf_params['fall']]
            o.petname = pet_name
            o.width = conf_params.get('width', 128)
            o.height = conf_params.get('height', 128)
            o.refresh = conf_params.get('refresh', 5)
            o.interact_speed = conf_params.get('interact_speed', 0.02) * 1000
            o.dropspeed = conf_params.get('dropspeed', 1.0)
            o.gravity = conf_params.get('gravity', 4.0)
            # 初始化随机动作
            random_act = []
            for act_array in conf_params['random_act']:
                random_act.append([act_dict[act] for act in act_array])
            o.random_act = random_act
            act_prob = conf_params.get('act_prob', None)
            if act_prob is None:
                act_prob = [1/len(random_act) for i in range(len(random_act))]
            else:
                act_prob = [act_prob[i]/sum(act_prob) for i in range(len(random_act))]

            total = 0
            for i in range(len(act_prob)):
                total += act_prob[i]
                o.act_prob.append(total)
            o.act_prob[-1] = 1.0

            return o


class Act:
    def __init__(self, images=(), act_num=1, need_move=False, direction=None, frame_move=10, frame_refresh=0.04):
        """
        动作
        :param images: 动作图像
        :param act_num 动作执行次数
        :param need_move: 是否需要移动
        :param direction: 移动方向
        :param frame_move 单帧移动距离
        :param frame_refresh 单帧刷新时间
        """
        self.images = images
        self.act_num = act_num
        self.need_move = need_move
        self.direction = direction
        self.frame_move = frame_move
        self.frame_refresh = frame_refresh

    @classmethod
    def init_act(cls, conf_param, pic_dict, pet_name):
        images = conf_param['images']
        img_dir = 'res/role/{}/action/{}'.format(pet_name, images)
        list_images = glob.glob('{}_*.png'.format(img_dir))
        n_images = len(list_images)
        img = []
        for i in range(n_images):
            img.append(pic_dict["%s_%s"%(images, i)])
        act_num = conf_param.get('act_num', 1)
        need_move = conf_param.get('need_move', False)
        direction = conf_param.get('direction', None)
        frame_move = conf_param.get('frame_move', 10)
        frame_refresh = conf_param.get('frame_refresh', 0.5)
        return Act(img, act_num, need_move, direction, frame_move, frame_refresh)


def tran_idx_img(start_idx: int, end_idx: int, pic_dict: dict) -> list:
    """
    转化坐标与图像
    :param start_idx: 开始坐标
    :param end_idx: 结束坐标
    :param pic_dict: 图像dict
    :return: 一个动作所有的图片list
    """
    res = []
    for i in range(start_idx, end_idx + 1):
        res.append(pic_dict[str(i)])
    return res