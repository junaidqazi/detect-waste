from efficientdet_lighning.efficientdet.anchors import AnchorLabeler, Anchors
from efficientdet_lighning.efficientdet.data import create_dataset, create_loader
from efficientdet_lighning.efficientdet.data import resolve_input_config
from efficientdet_lighning.efficientdet.evaluator import create_evaluator


def create_datasets_and_loaders(args, model_config):
    input_config = resolve_input_config(args, model_config=model_config)

    dataset_train, dataset_eval = create_dataset('DetectwasteCfg', "/dih4/dih4_2/wimlds/data/")

    # setup labeler in loader/collate_fn if not enabled in the model bench
    labeler = None
    bench_labeler = False
    if not bench_labeler:
        labeler = AnchorLabeler(
            Anchors.from_config(model_config), model_config.num_classes, match_threshold=0.5)

    distributed_sampler = True

    loader_train = create_loader(
        dataset=dataset_train,
        input_size=input_config['input_size'],
        batch_size=3,
        is_training=True,
        use_prefetcher=True,
        re_prob=0.2,
        re_mode='pixel',
        re_count=1,
        # color_jitter=args.color_jitter,
        # auto_augment=args.aa,
        interpolation='random' or input_config['interpolation'],
        fill_color=input_config['fill_color'],
        mean=input_config['mean'],
        std=input_config['std'],
        num_workers=8,
        distributed=False,
        pin_mem=True,
        anchor_labeler=labeler,
        distributed_sampler=distributed_sampler
    )

    loader_eval = create_loader(
        dataset_eval,
        input_size=input_config['input_size'],
        batch_size=8,
        is_training=False,
        use_prefetcher=True,
        interpolation=input_config['interpolation'],
        fill_color=input_config['fill_color'],
        mean=input_config['mean'],
        std=input_config['std'],
        num_workers=2,
        distributed=True,
        pin_mem=True,
        anchor_labeler=labeler,
        distributed_sampler=distributed_sampler
    )

    evaluator = create_evaluator('DetectwasteCfg', loader_eval.dataset,
                                 distributed=False, pred_yxyx=False)

    return loader_train, loader_eval, evaluator
