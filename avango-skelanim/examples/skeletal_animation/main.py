import avango
import avango.script
from avango.script import field_has_changed
# import avango.gua
import avango.gua.skelanim
from examples_common.GuaVE import GuaVE
import math

from CharacterControl import *
from CameraControl import *

bob = None
light2 = None
cubes = []



class GroundFollowing(avango.script.Script):
  InTransform = avango.gua.SFMatrix4()
  OutTransform = avango.gua.SFMatrix4()
  OutTransform.value = avango.gua.make_identity_mat()

  OffsetToGround = avango.SFFloat()
  MaxDistanceToGround = avango.SFFloat()
  SceneGraph = avango.gua.nodes.SceneGraph()

  def __init__(self):
    self.super(GroundFollowing).__init__()

    self.OffsetToGround.value = 0.0
    self.MaxDistanceToGround.value = 1000.0
    self.__ray = avango.gua.nodes.RayNode()


  # @field_has_changed(InTransform)
  def evaluate(self):
    global bob
    global light2
    global cubes

    in_translation = self.InTransform.value.get_translate()
    in_translation.y += self.OffsetToGround.value

    self.__ray.Transform.value = avango.gua.make_trans_mat(in_translation) *\
                                 avango.gua.make_rot_mat(-90, 1, 0, 0) *\
                                 avango.gua.make_scale_mat(1.0, 1.0, self.MaxDistanceToGround.value)

    results = self.SceneGraph.value.ray_test(
                                     self.__ray,
                                     avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT |
                                     avango.gua.PickingOptions.GET_POSITIONS)

    
    #intersection test geometry:
    '''tri_mesh_loader = avango.gua.nodes.TriMeshLoader()
    cube1 = tri_mesh_loader.create_geometry_from_file("cube",
                                        "data/objects/cone.obj",
                                        avango.gua.LoaderFlags.NORMALIZE_POSITION
                                        | avango.gua.LoaderFlags.NORMALIZE_SCALE)
    cube = tri_mesh_loader.create_geometry_from_file("cube",
                                        "data/objects/cone.obj",
                                        avango.gua.LoaderFlags.NORMALIZE_POSITION
                                        | avango.gua.LoaderFlags.NORMALIZE_SCALE)
    #cube.Transform.value = avango.gua.make_trans_mat(first_hit.WorldPosition.value) * avango.gua.make_scale_mat(0.01,0.01,0.01)
    #cube1.Transform.value = avango.gua.make_trans_mat(hit_world_trans) * avango.gua.make_scale_mat(0.01,1.0,0.01)
    #display ray of ray test:
    cube.Transform.value = avango.gua.make_trans_mat(in_translation) *\
                             avango.gua.make_rot_mat(-90, 1, 0, 0) *\
                             avango.gua.make_scale_mat(0.01, 0.01, self.MaxDistanceToGround.value * 0.5)
    if self.SceneGraph.value != None:
      self.SceneGraph.value.Root.value.Children.value.append(cube)
      #self.SceneGraph.value.Root.value.Children.value.append(cube1)
      cubes.append(cube)
      #cubes.append(cube1)
    while len(cubes)>300:
      tmp_cube = cubes.pop(0)
      self.SceneGraph.value.Root.value.Children.value.remove(tmp_cube)'''


    delta_trans = avango.gua.Vec3(0.0,0.0,0.0)

    if len(results.value) > 0:


      if bob and bob.Animation.value == "swim":
       bob.Animation.value = "run_fwd"

      first_hit = results.value[0]

      hit_world = first_hit.Object.value.Transform.value * avango.gua.make_trans_mat(first_hit.Position.value)
      
      hit_world_trans = hit_world.get_translate()
      #hit_world_trans = first_hit.WorldPosition.value

      new_pos = avango.gua.make_trans_mat(hit_world_trans)# * avango.gua.make_trans_mat(0.0,self.OffsetToGround.value, 0.0)

      if light2 != None:
        light2.Transform.value = new_pos * avango.gua.make_trans_mat(0.0,0.2,0.0)

      delta_trans = (new_pos.get_translate() - self.InTransform.value.get_translate())

    else:
      if bob and bob.Animation.value == "run_fwd":
       bob.Animation.value = "swim"

    delta_norm = avango.gua.Vec3(delta_trans.x,delta_trans.y,delta_trans.z)
    length = delta_norm.normalize()

    #self.OutTransform.value = self.OutTransform.value * avango.gua.make_trans_mat(delta_trans/3.0)#/3.0 smoothing(???)
    if length > 0.01:
      self.OutTransform.value = self.OutTransform.value * avango.gua.make_trans_mat(delta_norm*0.01)
    else:
      self.OutTransform.value = self.OutTransform.value * avango.gua.make_trans_mat(delta_trans)


    if math.fabs(delta_trans.y)<0.05 and bob.Animation.value == "land":
      bob.BlendingDuration.value = 0.25
      bob.Animation.value = "idle"



def start():

  global bob
  
  # setup scenegraph
  graph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

  loader = avango.gua.skelanim.nodes.SkeletalAnimationLoader()

  bob_nav = avango.gua.nodes.TransformNode(Name = "bob_nav")
  bob_ground = avango.gua.nodes.TransformNode(Name = "bob_ground")

  #bob = loader.create_geometry_from_file("bob", "data/objects/marine/mpplayer.md5mesh" ,
  bob = loader.create_geometry_from_file("bob", "data/objects/Necris/necris_male_ut4_SKELMESH.FBX" ,
         avango.gua.LoaderFlags.LOAD_MATERIALS
         |avango.gua.LoaderFlags.NORMALIZE_SCALE)

  bob.Transform.value = bob.Transform.value * avango.gua.make_rot_mat(-90.0,1.0,0.0,0.0)

  '''loader.load_animation(bob,
          "data/objects/marine/fists_idle.md5anim","idle", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob, "data/objects/marine/run.md5anim","run_fwd",
          avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/objects/marine/crouch.md5anim","crouch", avango.gua.LoaderFlags.DEFAULTS)'''

  loader.load_animation(bob,
          "data/animations/Idle_Ready_Rif.FBX","idle", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
         "data/animations/Run_Fwd_Rif.FBX","run_fwd", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
         "data/animations/Run_Bwd_Rif.FBX","run_bwd", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Taunt_PelvicThrust.FBX","taunt", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Swim_Fwd_Rif.FBX","swim", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Crouch_Idle_Ready_Rif.FBX","crouch", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Crouch_Fwd_Rif.FBX","crouch_fwd", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Crouch_Bwd_Rif.FBX","crouch_bwd", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Jump_Idle_Rif_Start.FBX","jump", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Jump_Idle_Rif_Loop.FBX","land", avango.gua.LoaderFlags.DEFAULTS)
  loader.load_animation(bob,
          "data/animations/Jump_Fwd_Rif.FBX","jump_fwd", avango.gua.LoaderFlags.DEFAULTS)


  bob_nav.Transform.value =  bob_nav.Transform.value * avango.gua.make_trans_mat(0.0,0.05,0.0) * avango.gua.make_scale_mat(0.2,0.2,0.2)

  bob.AnimationMode.value = 1

  bob_ground.Children.value = [bob_nav]
  bob_nav.Children.value = [bob]


  #environment:
  tri_mesh_loader = avango.gua.nodes.TriMeshLoader()

  medieval_harbour = tri_mesh_loader.create_geometry_from_file("medieval_harbour", "/opt/3d_models/architecture/medieval_harbour/town.obj",
                                            avango.gua.LoaderFlags.MAKE_PICKABLE|
                                            avango.gua.LoaderFlags.LOAD_MATERIALS)


  #medieval_harbour.Transform.value = medieval_harbour.Transform.value * avango.gua.make_trans_mat(0,0.57, -5)
  #medieval_harbour.Transform.value = medieval_harbour.Transform.value * avango.gua.make_trans_mat(0.0,0.0, -5.0)

  plane = tri_mesh_loader.create_geometry_from_file("cube",
                                            "data/objects/cube.obj",
                                            avango.gua.LoaderFlags.NORMALIZE_POSITION
                                            | avango.gua.LoaderFlags.NORMALIZE_SCALE
                                            | avango.gua.LoaderFlags.OPTIMIZE_GEOMETRY
                                            | avango.gua.LoaderFlags.MAKE_PICKABLE)

  plane.Transform.value *= avango.gua.make_scale_mat(3.0,0.01,10.0) *  avango.gua.make_trans_mat(0, -3, 0)


  plane.Transform.value *= avango.gua.make_scale_mat(1.0,1.0,1.0) *  avango.gua.make_trans_mat(0, 0, 0)

  light = avango.gua.nodes.PointLightNode(
                Name = "light",
                Color = avango.gua.Color(0.1, 0.1, 0.1),
                Brightness = 1.0,
                EnableShadows = True)

  light.Transform.value = avango.gua.make_trans_mat(0.0, 2.0, 2.0) * avango.gua.make_scale_mat(2100, 2100, 2100)

  global light2
  light2 = avango.gua.nodes.PointLightNode(
                Name = "light2",
                Color = avango.gua.Color(1.0, 1.0, 1.0),
                Brightness = 1.0,
                EnableShadows = True)


  size = avango.gua.Vec2ui(2560, 1440)

  window = avango.gua.nodes.GlfwWindow(
    Size = size,
    LeftResolution = size
  )

  cam = avango.gua.nodes.CameraNode(LeftScreenPath = "/screen",
                                    SceneGraph = "scenegraph",
                                    Resolution = size,
                                    OutputWindowName = "window")

  pipeline_description = avango.gua.nodes.PipelineDescription(
      Passes = [
            avango.gua.nodes.TriMeshPassDescription(),
            avango.gua.nodes.LightVisibilityPassDescription(),
            avango.gua.skelanim.nodes.SkeletalAnimationPassDescription(),
            avango.gua.nodes.ResolvePassDescription()
          ])

  cam.PipelineDescription.value = pipeline_description

  cam.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.0)
  cam.FarClip.value = 10000

  screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 0.8, Height = 0.45)
  screen.Children.value = [cam, light]
  screen.Transform.value = avango.gua.make_trans_mat(0, 0.1, -2)

  graph.Root.value.Children.value = [bob_ground, medieval_harbour ,screen,light2]

  avango.gua.register_window("window", window)

  #setup viewer
  viewer = avango.gua.nodes.Viewer()
  #viewer.CameraNodes.value = [cam]
  viewer.SceneGraphs.value = [graph]
  viewer.Windows.value = [window]


  # setup character control
  character_control = CharacterControl()
  character_control.my_constructor(bob,bob_nav,window)

  # A
  character_control.bind_transformation(65, avango.gua.make_rot_mat(4.0, 0.0, 1.0,0.0))
  # D
  character_control.bind_transformation(68, avango.gua.make_rot_mat(-4.0, 0.0, 1.0,0.0))

  # W
  character_control.key_down(87, "idle","run_fwd")
  character_control.key_up(87, "run_fwd","idle")
  character_control.key_down(87, "crouch","crouch_fwd")
  character_control.key_up(87, "crouch_fwd","crouch")
  character_control.key_up(87, "jump_fwd","idle")

  # S
  character_control.key_down(83, "idle","run_bwd")
  character_control.key_up(83, "run_bwd","idle")
  character_control.key_down(83, "crouch","crouch_bwd")
  character_control.key_up(83, "crouch_bwd","crouch")

  # C
  character_control.key_down(67, "idle","crouch",0.2)
  character_control.key_up(67, "crouch","idle",0.4)
  character_control.key_down(67, "run_fwd","crouch_fwd")
  character_control.key_up(67, "crouch_fwd","run_fwd")
  character_control.key_down(67, "run_bwd","crouch_bwd")
  character_control.key_up(67, "crouch_bwd","run_bwd")

  # K
  character_control.key_down(75, "idle","taunt")
  character_control.key_up(75, "taunt","idle")

  # SPACE BAR
  character_control.key_down(32, "idle","jump",0.01)
  character_control.key_down(32, "run_fwd","jump_fwd",0.01)
  character_control.key_up(32, "jump","land",0.25)
  character_control.key_up(32, "jump","idle",0.01)
  character_control.key_up(32, "jump_fwd","run_fwd")
  #character_control.bind_transformation(32, avango.gua.make_trans_mat(0.0, 0.1, 0.0))

  character_control.bind_translation("run_fwd",avango.gua.Vec3(0.0,0.0,0.05))
  character_control.bind_translation("run_bwd",avango.gua.Vec3(0.0,0.0,-0.05))
  character_control.bind_translation("swim",avango.gua.Vec3(0.0,0.0,0.05))
  character_control.bind_translation("crouch_fwd",avango.gua.Vec3(0.0,0.0,0.02))
  character_control.bind_translation("crouch_bwd",avango.gua.Vec3(0.0,0.0,-0.02))
  character_control.bind_translation("jump",avango.gua.Vec3(0.0, 0.08, 0.0))
  character_control.bind_translation("jump_fwd",avango.gua.Vec3(0.0, 0.08, 0.04))

  #wall detection:
  character_control.activate_wall_detection(0.13,"idle",graph)

  # setup camera control
  camera_control = CameraControl()
  camera_control.my_constructor(screen,bob,window)

  # setup ground following
  ground_following = GroundFollowing(
    SceneGraph = graph,
    OffsetToGround = 0.1,
    MaxDistanceToGround = 1.0
  )

  ground_following.InTransform.connect_from(bob.WorldTransform)

  bob_ground.Transform.connect_from(ground_following.OutTransform)

  timer = avango.nodes.TimeSensor()
  character_control.TimeIn.connect_from(timer.Time)
  camera_control.TimeIn.connect_from(timer.Time)

  guaVE = GuaVE()
  guaVE.start(locals(), globals())

  viewer.run()

if __name__ == '__main__':
  start()

