_base_ = ["../_base_/default_runtime.py", "../_base_/datasets/aihub.py"]
evaluation = dict(interval=5, metric="mAP", save_best="AP")

optimizer = dict(
    type="Adam",
    lr=5e-5,
)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy="step", warmup="linear", warmup_iters=500, warmup_ratio=0.001, step=[17, 20]
)
total_epochs = 21
channel_cfg = dict(
    num_output_channels=12,
    dataset_joints=12,
    dataset_channel=[
        list(range(12)),
    ],
    inference_channel=[
        range(12),
    ],
)

# model settings
model = dict(
    type="TopDown",
    pretrained="torchvision://resnet50",
    backbone=dict(type="ResNet", depth=50),
    keypoint_head=dict(
        type="TopdownHeatmapSimpleHead",
        in_channels=2048,
        out_channels=channel_cfg["num_output_channels"],
        loss_keypoint=dict(type="JointsMSELoss", use_target_weight=True),
    ),
    train_cfg=dict(),
    test_cfg=dict(
        flip_test=True, post_process="default", shift_heatmap=True, modulate_kernel=11
    ),
)

data_cfg = dict(
    image_size=[192, 256],
    heatmap_size=[48, 64],
    num_output_channels=channel_cfg["num_output_channels"],
    num_joints=channel_cfg["dataset_joints"],
    dataset_channel=channel_cfg["dataset_channel"],
    inference_channel=channel_cfg["inference_channel"],
    soft_nms=False,
    nms_thr=1.0,
    oks_thr=0.9,
    vis_thr=0.2,
    use_gt_bbox=True,
    det_bbox_thr=0.0,
    bbox_file="",
)

train_pipeline = [
    dict(type="LoadImageFromFile"),
    dict(type="TopDownGetBboxCenterScale", padding=1.25),
    dict(type="TopDownRandomShiftBboxCenter", shift_factor=0.16, prob=0.3),
    dict(type="TopDownRandomFlip", flip_prob=0.5),
    dict(type="TopDownHalfBodyTransform", num_joints_half_body=8, prob_half_body=0.3),
    dict(type="TopDownGetRandomScaleRotation", rot_factor=40, scale_factor=0.5),
    dict(type="TopDownAffine"),
    dict(type="ToTensor"),
    dict(type="NormalizeTensor", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    dict(type="TopDownGenerateTarget", sigma=2),
    dict(
        type="Collect",
        keys=["img", "target", "target_weight"],
        meta_keys=[
            "image_file",
            "joints_3d",
            "joints_3d_visible",
            "center",
            "scale",
            "rotation",
            "bbox_score",
            "flip_pairs",
        ],
    ),
]

val_pipeline = [
    dict(type="LoadImageFromFile"),
    dict(type="TopDownGetBboxCenterScale", padding=1.25),
    dict(type="TopDownAffine"),
    dict(type="ToTensor"),
    dict(type="NormalizeTensor", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    dict(
        type="Collect",
        keys=["img"],
        meta_keys=[
            "image_file",
            "center",
            "scale",
            "rotation",
            "bbox_score",
            "flip_pairs",
        ],
    ),
]

test_pipeline = val_pipeline

data_root = "data/aihub"
dataset_type = "TopDownAihubDataset"
data = dict(
    samples_per_gpu=32,
    workers_per_gpu=2,
    val_dataloader=dict(samples_per_gpu=32),
    test_dataloader=dict(samples_per_gpu=32),
    train=dict(
        type=dataset_type,
        ann_file=f"{data_root}/annotations/aihub_train.json",
        img_prefix=f"{data_root}/images/",
        data_cfg=data_cfg,
        pipeline=train_pipeline,
        dataset_info={{_base_.dataset_info}},
    ),
    val=dict(
        type="TopDownCocoDataset",
        ann_file=f"{data_root}/annotations/aihub_test.json",
        img_prefix=f"{data_root}/images/",
        data_cfg=data_cfg,
        pipeline=val_pipeline,
        dataset_info={{_base_.dataset_info}},
    ),
    test=dict(
        type="TopDownCocoDataset",
        ann_file=f"{data_root}/annotations/aihub_test.json",
        img_prefix=f"{data_root}/images/",
        data_cfg=data_cfg,
        pipeline=test_pipeline,
        dataset_info={{_base_.dataset_info}},
    ),
)

load_from = "https://download.openmmlab.com/mmpose/top_down/resnet/res50_coco_256x192-ec54d7f3_20200709.pth"
