from models.post import PostModel


def create_posts(user_list):

    return [
        # Post 1
        PostModel(
            title="GIVE ME YOUR MONEY course",
            description="GIVEEEEE MEEEEEE!",
            image_url="https://live.staticflickr.com/65535/17123251389_80282733ce_z.jpg",
            institute_id=user_list[3].id  # Institution user
        ),
        
        # Post 2
        PostModel(
            title="Examp Prep",
            description="Same,Same But Different Exam Prep",
            image_url="https://i.imgur.com/TX2e5sy.jpeg",
            institute_id=user_list[3].id  # Institution user
        ),

        # Post 3
        PostModel(
            title="CHUM CHUM Exam Prep",
            description="Need Help! ? CHUM CHUM for one more thing",
            image_url="https://i.imgur.com/FQdComk.jpeg",
            institute_id=user_list[3].id  # Institution user
        ),
    ]
