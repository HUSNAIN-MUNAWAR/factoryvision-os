from .base import InspectionWorkflowPlugin
class ContaminationRatioWorkflow(InspectionWorkflowPlugin):
    name='community-contamination-ratio'; task='segmentation'; classes=('steel','copper')
    def decide(self,observations):
        total=sum(x['area'] for x in observations) or 1; copper=sum(x['area'] for x in observations if x['class_name']=='copper'); ratio=copper/total
        return {'action':'reject' if ratio>=.08 else 'review' if ratio>=.03 else 'pass','copper_area_ratio':ratio}
